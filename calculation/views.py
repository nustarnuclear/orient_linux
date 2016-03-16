import os
import time
from django.core.files import File
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from calculation.functions import position_node_by_excel,get_same_group_users
from calculation.serializers import EgretTaskSerializer,MultipleLoadingPatternSerializer
from tragopan.models import Plant,UnitParameter,Cycle
from calculation.models import EgretTask,MultipleLoadingPattern
from xml.dom import minidom
import signal
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.parsers import FileUploadParser
from rest_framework_xml.parsers import XMLParser
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from orient.celery import app
from datetime import datetime
import shutil
import tempfile
@api_view(('POST','GET','DELETE','PUT'))
@parser_classes((FileUploadParser,XMLParser))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def egret_task(request,format=None):
    if request.method == 'DELETE':
        request_user=request.user
        query_params=request.query_params
        operation_type=int(query_params['operation_type'])
        task_pk=query_params['pk']
        task=EgretTask.objects.get(pk=task_pk)
        #stop operation
        if operation_type==1:
            
            #from orient.celery import app
            #calculation_identity=query_params['calculation_identity']
            pid=int(query_params['pid'])
            #app.control.revoke(calculation_identity,terminate=True)
            os.kill(pid,signal.SIGKILL)
            try:
                
                task=EgretTask.objects.get(pk=task_pk)
                suspend_user=task.user
                #check if you have delete permission
                if request_user!=suspend_user:
                    error_message={'error_message':"you cannot stop others' task"}
                    return Response(data=error_message,status=550)
    
            except Exception as e:
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
            while True:
                if task.task_status==4:
                    task.task_status=3
                    task.save()
                    break
                else:
                    time.sleep(1)
                    task.refresh_from_db()
                    
            return Response(data={'sucess_message':'stop operation finished'},status=200)
            
            
        #delete operation      
        elif operation_type==2:
            
            try:
                delete_user=task.user
                #check if you have delete permission
                if request_user!=delete_user:
                    error_message={'error_message':"you cannot delete others' task"}
                    return Response(data=error_message,status=550)
                    
                task.delete()     
                return Response(data={'sucess_message':'delete operation finished'},status=200)
            except Exception as e:
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
        # cancel operation
        elif operation_type==3:
            try:
                calculation_identity=task.calculation_identity
                app.control.revoke(calculation_identity)
                task.task_status=5
                task.end_time=datetime.now()
                task.save()
                return Response(data={'sucess_message':'cancel operation finished'},status=200)
            
            except Exception as e:
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
            
        else:
            error_message={'error_message':'the operation type is not supported yet'}
            return Response(data=error_message,status=404)
        
        
     
    if request.method == 'GET':
        try:
            query_params=request.query_params
            pk=query_params['pk'] 
            loading_pattern=MultipleLoadingPattern.objects.get(pk=pk)
            user=request.user
            same_group_users=get_same_group_users(user)  
                 
            task_list=EgretTask.objects.filter(Q(user__in=same_group_users)&Q(visibility=2)|Q(user=user)|Q(visibility=3),Q(loading_pattern=loading_pattern)|(Q(task_type='SEQUENCE')&Q(pre_egret_task__loading_pattern=loading_pattern)))
            if task_list is None:
                return Response(data={})
            
            serializer = EgretTaskSerializer(task_list,many=True)
            return Response(data=serializer.data)
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
    if request.method == 'POST':
        try:
            query_params=request.query_params
            data=request.data
            task_name=query_params['task_name']
            task_type=query_params['task_type']
            remark=query_params['remark']
            
            visibility=int(query_params['visibility'])
            countdown=int(query_params['countdown'])
            user=request.user
            input_file=data['file']
            
            #get pre egret task
            pre_task=EgretTask.objects.get(pk=query_params['pre_pk']) if 'pre_pk' in query_params else None 
            if pre_task and task_type=='SEQUENCE':
                #lock the pre egrt task when performing sequence calculation
                if task_type=='SEQUENCE':
                    pre_task.locked=True
                    pre_task.save()
                
            #get loading pattern pk
            loading_pattern=MultipleLoadingPattern.objects.get(pk=query_params['pk']) if 'pk' in query_params else None 
            
            
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)      
            
        #start creating egret task
        try:
            task_instance=EgretTask(task_name=task_name,task_type=task_type,user=user,remark=remark,egret_input_file=input_file,loading_pattern=loading_pattern,pre_egret_task=pre_task,visibility=visibility)
            task_instance.full_clean()
            task_instance.save()
            current_workdirectory=task_instance.get_cwd()
            task_instance.save()
            
            #change directory to current task directory
            os.chdir(current_workdirectory)
            
            #generate loading pattern xml
            task_instance.generate_loading_pattern_xml()
           
            #generate myegret xml
            task_instance.generate_runegret_xml()
       
            #copy the files to current working directory
            task_instance.cp_lp_res_file()
                
            #begin egret calculation
            task_instance.start_calculation(countdown=countdown)
        
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
        
        success_message={'pk':task_instance.pk,'task_name':task_name,'task_type':task_type,'get_input_filename':task_instance.get_input_filename()}
        success_message['egret_input_file']=task_instance.egret_input_file.url
        success_message['success_message']='your request has been handled successfully'
        
        if countdown!=0:
            return Response(data=success_message,status=200)
        
        #wait until myegret.log exists
        myegret_log=os.path.join(current_workdirectory,'myegret.log')
        log_status=os.path.isfile(myegret_log)    
        log_index=0
        max_circle=100
        while not log_status:
            time.sleep(0.1)
            log_index +=1
            log_status=os.path.isfile(myegret_log)
            if log_index==max_circle:
                break
        return Response(data=success_message,status=200)
        
    if request.method =='PUT':
        query_params=request.query_params
        
        try:
            #to represent the action
            update_type=query_params['update_type']
            task_pk=int(query_params['pk'])
            task_instance=EgretTask.objects.get(pk=task_pk)
            #1 reprsents you want to change visibility or authorized
            if int(update_type)==1:
                authorized=query_params['authorized']
                task_name=query_params['task_name']
                if not request.user.is_superuser:
                    error_message={'error_message':"you have no permission"}
                    return Response(data=error_message,status=550)
                    
                task_instance.authorized=int(authorized)
                task_instance.task_name=task_name
                task_instance.save()          
                success_message={'success_message':'your request has been handled successfully'}
                return Response(data=success_message,status=200,)
            
            #2 represent that you want to recalculation the task 
            elif int(update_type)==2:
                
                assert task_instance.locked==False, 'The task to be recalculated is locked'
                
                data=request.data
                input_file=data['file']
                remark=query_params['remark']
                countdown=int(query_params['countdown'])
                task_instance.recalculation_depth=task_instance.recalculation_depth+1
                task_instance.egret_input_file=input_file
                task_instance.remark=remark
                task_instance.task_status=0
                task_instance.start_time=None
                task_instance.end_time=None
                task_instance.save()
                
                #prepare for calculation
                current_workdirectory=task_instance.get_cwd()
                os.chdir(current_workdirectory)
                #generate myegret xml
                
                task_instance.generate_runegret_xml(restart=1)
                
                task_instance.start_calculation(countdown=countdown)
                
                success_message={'success_message':'your request has been handled successfully','get_input_filename':task_instance.get_input_filename()}
                return Response(data=success_message,status=200,)
                
            #3 represent that you want to deepcopy the task 
            elif int(update_type)==3: 
                cwd=task_instance.get_cwd()
                name=task_instance.task_name
                task_instance.pk=None
                new_name=query_params['task_name']
                task_instance.task_name=new_name
                task_instance.egret_input_file.name=task_instance.egret_input_file.name.replace(name,new_name)
                task_instance.save()
                
                #copy the files
                new_cwd=os.path.join(os.path.dirname(cwd),new_name)
                shutil.copytree(cwd, new_cwd, symlinks=True,)
                
                success_message={'success_message':'your request has been handled successfully',}
                return Response(data=success_message,status=200,)
            
            else:
                error_message={'error_message':'the updated type is not supported yet'}
                return Response(data=error_message,status=404)
            
                
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
            
        
        
@api_view(('POST','PUT','GET','DELETE'))
@parser_classes((FileUploadParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def multiple_loading_pattern(request,format=None):
    query_params=request.query_params
    if request.method=='DELETE':
        try:
            pk=query_params['pk']
            mlp=MultipleLoadingPattern.objects.get(pk=pk)
                
            if request.user!=mlp.user and not request.user.is_superuser or mlp.authorized:
                error_message={'error_message':"you have no permission"}
                return Response(data=error_message,status=550)
            mlp.delete()
            success_message={'success_message':'your request has been handled successfully'}
            return Response(data=success_message,status=200,)
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
            
        
    try:
        
        plantname=query_params['plant']
        unit_num=query_params['unit']
        cycle_num=query_params['cycle']
    
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
    except Exception as e:
        error_message={'error_message':e}
        return Response(data=error_message,status=404)
    
        
    data=request.data
 
    if request.method == 'POST':
        file=data['file']
        name=request.query_params['name']
        try:
            pre_pk=request.query_params['pre_pk']
            
            pre_loading_pattern=MultipleLoadingPattern.objects.get(pk=pre_pk)
            mlp=MultipleLoadingPattern(user=request.user,name=name,xml_file=file,cycle=cycle,pre_loading_pattern=pre_loading_pattern)
        except:
            mlp=MultipleLoadingPattern(user=request.user,name=name,xml_file=file,cycle=cycle)
        mlp.save()
        success_message={'success_message':'your request has been handled successfully','pk':mlp.pk}
        return Response(data=success_message,status=200)
    
    if request.method=='GET':
        user=request.user
        same_group_users=get_same_group_users(user)   
        mlps=MultipleLoadingPattern.objects.filter(Q(user__in=same_group_users)&Q(visibility=2)|Q(user=user)|Q(visibility=3),cycle=cycle)
       
        if mlps.exists():
            serializer = MultipleLoadingPatternSerializer(mlps,many=True)
            return Response(data=serializer.data,status=200)  
        else:
            return Response(data={},status=200)
    
    if request.method == 'PUT':
        
        file=data['file']
        name=request.query_params['name']
        try:
            
            loading_pattern=MultipleLoadingPattern.objects.get(name=name,cycle=cycle,user=request.user,)
        except Exception as e:
            print(e)
            return Response(data={'error_message':e},status=404)
        loading_pattern.xml_file.delete()
        loading_pattern.xml_file=file
        loading_pattern.save()
        success_message={'success_message':'your request has been handled successfully'}
        return Response(data=success_message,status=200)
    
@api_view(('POST',))
@parser_classes((XMLParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def upload_loading_pattern(request,format=None):
    try:
        query_params=request.query_params
        plantname=query_params['plant']
        unit_num=query_params['unit']
        cycle_num=query_params['cycle']
    
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get_or_create(unit=unit,cycle=cycle_num)[0]
    except Exception as e:
        error_message={'error_message':e}
        print(e)
        return Response(data=error_message,status=404)
    
    
    
    if request.method == 'POST':
        try:
            name=query_params['name']
            data=request.data
        
            doc = minidom.Document()
        
            loading_pattern_xml = doc.createElement("loading_pattern")
            loading_pattern_xml.setAttribute('cycle_num', str(cycle_num))
            loading_pattern_xml.setAttribute('plant_name', str(plantname))
            loading_pattern_xml.setAttribute('unit_num', str(unit_num))
            doc.appendChild(loading_pattern_xml)
            fuel_xml = doc.createElement("fuel")
            loading_pattern_xml.appendChild(fuel_xml)
            for item in data:
                [n,row,column,position_or_type]=item.split()
                
                nth_cycle=cycle.get_nth_cycle(int(n))
                try:
     
                    position_node=position_node_by_excel(nth_cycle,int(row),int(column),position_or_type)
                except Exception as e:
                    error_message={'error_message':e}
                    print(error_message)
                    return Response(data=error_message,status=404)
            
                fuel_xml.appendChild(position_node)
            
            #create a temporary file 
            f = tempfile.TemporaryFile(mode='w+')
            doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
            
            mlp=MultipleLoadingPattern.objects.create(name=name,cycle=cycle,xml_file=File(f),user=request.user,)
            print('finished')
            f.close()
                
            success_message={'success_message':'your request has been handled successfully','pk':mlp.pk,'url':mlp.xml_file.url}
            return Response(data=success_message,status=200)
        
        except Exception as e:
            error_message={'error_message':e}
            print(e)
            return Response(data=error_message,status=404)
        

@api_view(('PUT',))
@parser_classes((XMLParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def extra_updating(request,format=None):
    '''the model to be authorized: 
        1->EgretTask
        2->MultipleLoadingPattern
        
       the update type:
       1->visibility
       2->authorized
       
       the value to update:
       
       pk needed to target a specified model instance
    '''
    if request.method =='PUT':
        query_params=request.query_params
        try:
            target_type=int(query_params['target_type'])
            update_type=int(query_params['update_type'])
            update_value=int(query_params['update_value'])
            pk=int(query_params['pk'])
            
            #target which model
            if target_type==1:
                target=EgretTask.objects.get(pk=pk)
            elif target_type==2:
                target=MultipleLoadingPattern.objects.get(pk=pk)
            else:
                error_message={'error_message':'the target type is not supported'}
                print(error_message)
                return Response(data=error_message,status=404)
                
            #visibility or authorized
            if update_type==1:
    
                if target.user!=request.user:
                    error_message={'error_message':"you have no permission"}
                    print(error_message)
                    return Response(data=error_message,status=550)
                
                target.visibility=update_value
                target.save()
            
            elif update_type==2:
                
                if not request.user.is_superuser:
                    error_message={'error_message':"you have no permission"}
                    print(error_message)
                    return Response(data=error_message,status=550)
                
                target.authorized=update_value
                target.save()  
            else:
                error_message={'error_message':'the update type is not supported'}
                print(error_message)
                return Response(data=error_message,status=404)
                        
            success_message={'success_message':'your request has been handled successfully'}
            return Response(data=success_message,status=200,)
            
        except Exception as e:
            error_message={'error_message':e}
            print(e)
            return Response(data=error_message,status=404)
        

        

