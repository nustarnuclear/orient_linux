import os
import time
from django.conf import settings
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


    

    

    
    
 
@api_view(('POST','GET','DELETE','PUT'))
@parser_classes((FileUploadParser,XMLParser))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def egret_task(request,format=None):
    if request.method == 'DELETE':
        request_user=request.user
        query_params=request.query_params
        #stop operation
        if 'pid' in query_params:
            
            #from orient.celery import app
            #calculation_identity=query_params['calculation_identity']
            pid=int(query_params['pid'])
            #app.control.revoke(calculation_identity,terminate=True)
            os.kill(pid,signal.SIGKILL)
            try:
                task_pk=query_params['pk']
                stopped_task=EgretTask.objects.get(pk=task_pk)
                suspend_user=stopped_task.user
                #check if you have delete permission
                if request_user!=suspend_user:
                    error_message={'error_message':"you cannot stop others' task"}
                    return Response(data=error_message,status=550)
    
            except Exception as e:
                print(e)
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
            while True:
                if stopped_task.task_status==4:
                    stopped_task.task_status=3
                    stopped_task.save()
                    break
                else:
                    time.sleep(3)
                    stopped_task.refresh_from_db()
                    
            print('stop operation finished')
            return Response(data={'sucess_message':'stop operation finished'},status=200)
            
            
        #delete operation      
        if 'pk' in query_params:
            task_pk=query_params['pk']
            
            
            try:
                delete_task=EgretTask.objects.get(pk=task_pk)
                delete_user=delete_task.user
                #check if you have delete permission
                if request_user!=delete_user:
                    error_message={'error_message':"you cannot delete others' task"}
                    return Response(data=error_message,status=550)
                    
                delete_task.delete()     
                return Response(data={'sucess_message':'delete operation finished'},status=200)
            except Exception as e:
                print(e)
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
        
     
    if request.method == 'GET':
        try:
            query_params=request.query_params
            pk=query_params['pk']
            
            loading_pattern=MultipleLoadingPattern.objects.get(pk=pk)
            user=request.user
            same_group_users=get_same_group_users(user)  
                 
            task_list=EgretTask.objects.filter(Q(user__in=same_group_users)&Q(visibility=2)|Q(user=user)|Q(visibility=3),loading_pattern=loading_pattern)
            if task_list is None:
                return Response(data={})
            
            serializer = EgretTaskSerializer(task_list,many=True)
            return Response(data=serializer.data)
        except Exception as e:
            print(e)
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
    if request.method == 'POST':
        try:
            query_params=request.query_params
            data=request.data
            task_name=query_params['task_name']
            task_type=query_params['task_type']
            remark=query_params['remark']
            pk=query_params['pk']
            visibility=int(query_params['visibility'])
            countdown=int(query_params['countdown'])
            user=request.user
            input_file=data['file']

            loading_pattern=MultipleLoadingPattern.objects.get(pk=pk)
            #reactor_model_name=unit.reactor_model.name
            cycle=loading_pattern.cycle
            cycle_num=cycle.cycle
    
            
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
        #previous egret task
        if 'pre_pk' in query_params:
            pre_pk=query_params['pre_pk'] 
            try:
                pre_task=EgretTask.objects.get(pk=pre_pk)
            except Exception as e:
                error_message={'error_message':e}
                print(e)
                return Response(data=error_message,status=404)
        elif cycle_num==1:
            pre_task=None
        else:
            error_message={'error_message':'you need to provide a previous egret task'}
            print(error_message)
            return Response(data=error_message,status=404) 
            
        #check if the task_name repeated
        try:
            EgretTask.objects.get(task_name=task_name,user=user,loading_pattern=loading_pattern)
            error_message={'error_message':'the taskname already exists'}
            return Response(data=error_message,status=404)
        except:
            pass
            
        #start creating egret task
        try:
            task_instance=EgretTask(task_name=task_name,task_type=task_type,user=user,remark=remark,egret_input_file=input_file,loading_pattern=loading_pattern,pre_egret_task=pre_task,visibility=visibility)
            task_instance.full_clean()
            task_instance.save()
            current_workdirectory=task_instance.get_cwd()
            workspace_dir=os.path.join(current_workdirectory,'.workspace')
            xml_path=os.path.join(workspace_dir,task_instance.get_lp_res_filename()+'.xml')
            task_instance.result_path=xml_path
            task_instance.save()
            
            #change directory to current task directory
            os.chdir(current_workdirectory)
            
            #generate loading pattern xml
            task_instance.generate_loading_pattern_xml()
           
            #generate runegret xml
            task_instance.generate_runegret_xml()
       
            #copy the files to current working directory
            task_instance.cp_lp_res_file()
                
            #begin egret calculation
            task_instance.start_calculation(countdown=countdown)
        
        except Exception as e:
            error_message={'error_message':e}
            print(e)
            return Response(data=error_message,status=404)
        
        
        success_message={'pk':task_instance.pk,'task_name':task_name,'task_type':task_type}
        success_message['egret_input_file']=task_instance.egret_input_file.url
        success_message['success_message']='your request has been handled successfully'
        time.sleep(1)
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
                    print(error_message)
                    return Response(data=error_message,status=550)
                    
                task_instance.authorized=int(authorized)
                task_instance.task_name=task_name
                task_instance.save()          
                success_message={'success_message':'your request has been handled successfully'}
                return Response(data=success_message,status=200,)
            
            #2 represent that you want to recalculation the task 
            elif int(update_type)==2:
                
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
                #generate runegret xml
                
                task_instance.generate_runegret_xml(restart=1)
                
                task_instance.start_calculation(countdown=countdown)
                
                success_message={'success_message':'your request has been handled successfully'}
                return Response(data=success_message,status=200,)  
            
            else:
                error_message={'error_message':'the updated type is not supported yet'}
                print(error_message)
                return Response(data=error_message,status=404)
            
                
        except Exception as e:
            error_message={'error_message':e}
            print(e)
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
        
        tmp_dir=settings.TMP_DIR    
        f = open(os.path.join(tmp_dir,'upload_loading_pattern.xml'),"w+")
        doc.writexml(f)
        
        mlp=MultipleLoadingPattern.objects.create(name=name,cycle=cycle,xml_file=File(f),user=request.user,)
        print('finished')
        f.close()
            
        success_message={'success_message':'your request has been handled successfully','pk':mlp.pk,'url':mlp.xml_file.url}
        return Response(data=success_message,status=200)
    

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
    
