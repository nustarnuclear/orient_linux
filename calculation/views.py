import os
import shutil
from django.conf import settings
from django.core.files import File
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from calculation.functions import position_node_by_excel,get_same_group_users
from calculation.serializers import EgretTaskSerializer,MultipleLoadingPatternSerializer
from tragopan.models import Plant,UnitParameter,Cycle
from calculation.models import EgretTask,MultipleLoadingPattern,EgretInputXML
from xml.dom import minidom
from subprocess import Popen
from rest_framework import status
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.parsers import FileUploadParser
from rest_framework_xml.parsers import XMLParser
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
        
 
 
@api_view(('POST','GET','DELETE','PUT'))
@parser_classes((FileUploadParser,XMLParser))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def generate_egret_task(request,format=None):
    if request.method == 'DELETE':
        request_user=request.user
        query_params=request.query_params
        task_pk=query_params['pk']
        
        try:
            delete_task=EgretTask.objects.get(pk=task_pk)
            delete_user=delete_task.user
            #check if you have delete permission
            if request_user!=delete_user:
                error_message={'error_message':"you cannot delete others' task"}
                return Response(data=error_message,status=404)
                
            delete_task.delete()     
            return Response(data={'sucess_message':'delete finished'},status=200)
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
            return Response(data=serializer.data,headers={'cmd':2})
        except Exception as e:
            print(e)
            error_message={'error_message':e}
            return Response(data=error_message,status=404,headers={'cmd':2})
        
    if request.method == 'POST':
        query_params=request.query_params
        data=request.data
        task_name=query_params['task_name']
        task_type=query_params['task_type']
        remark=query_params['remark']
        pk=query_params['pk']
        visibility=int(query_params['visibility'])
        user=request.user
        input_file=data['file']
        
        try:
            loading_pattern=MultipleLoadingPattern.objects.get(pk=pk)
            #reactor_model_name=unit.reactor_model.name
            cycle=loading_pattern.cycle
            cycle_num=cycle.cycle
            unit=cycle.unit
            unit_num=unit.unit
            plant=unit.plant
            plant_name=plant.abbrEN
            core_id="{}_U{}".format(plant_name,unit_num)
            egret_input_xml=EgretInputXML.objects.get(unit=unit)
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
            task_instance=EgretTask.objects.create(task_name=task_name,task_type=task_type,user=user,remark=remark,egret_input_file=input_file,loading_pattern=loading_pattern,pre_egret_task=pre_task,visibility=visibility)
            current_workdirectory=task_instance.get_cwd()
            workspace_dir=os.path.join(current_workdirectory,'.workspace')
            xml_path=os.path.join(workspace_dir,task_instance.get_lp_res_filename()+'.xml')
            task_instance.result_path=xml_path
            task_instance.save()
            
            media_root=settings.MEDIA_ROOT
            plant_dir=os.path.join(media_root, plant_name)
            ibis_dir=os.path.join(plant_dir,'ibis_files')
            
            #change directory to current task directory
            os.chdir(current_workdirectory)
            #loading pattern xml
            #from database loading pattern xml
           
            dividing_point=loading_pattern.get_dividing_point()
           
            custom_fuel_nodes=loading_pattern.get_custom_fuel_nodes()
            
            loading_pattern_doc=egret_input_xml.generate_loading_pattern_doc(max_cycle=dividing_point.cycle.cycle)
            loading_pattern_node=loading_pattern_doc.documentElement
           
            
            for custom_fuel_node in custom_fuel_nodes:
                loading_pattern_node.appendChild(custom_fuel_node)
            #custom loading pattern xml
            
            loading_pattern_file=open('loading_pattern.xml','w')
            loading_pattern_doc.writexml(loading_pattern_file)
            loading_pattern_file.close()
            
            
            #generate runegret xml
            doc=minidom.Document()
            run_egret_xml=doc.createElement('run_egret')
            doc.appendChild(run_egret_xml)
            run_egret_xml.setAttribute('core_id', core_id)
            run_egret_xml.setAttribute('cycle',str(cycle_num))
            #xml path
            base_core_path=egret_input_xml.base_core_path
            base_component_path=egret_input_xml.base_component_path
            base_core_xml=doc.createElement('base_core')
            base_core_xml.appendChild(doc.createTextNode(base_core_path))
            run_egret_xml.appendChild(base_core_xml)
            base_component_xml=doc.createElement('base_component')
            base_component_xml.appendChild(doc.createTextNode(base_component_path))
            run_egret_xml.appendChild(base_component_xml)
            #loading pattern is in current working directory
            loading_pattern_xml=doc.createElement('loading_pattern')
            loading_pattern_xml.appendChild(doc.createTextNode('loading_pattern.xml'))
            run_egret_xml.appendChild(loading_pattern_xml)
            #cycle_depl
            cycle_depl_xml=doc.createElement('cycle_depl')
            cycle_depl_file=os.path.basename(task_instance.egret_input_file.name)
            cycle_depl_xml.appendChild(doc.createTextNode(cycle_depl_file))
            run_egret_xml.appendChild(cycle_depl_xml)
            
            #ibis directory
            ibis_path_xml=doc.createElement('ibis_dir')
            ibis_path_xml.appendChild(doc.createTextNode(ibis_dir))
            run_egret_xml.appendChild(ibis_path_xml)
            input_filename='U{}C{}.xml'.format(unit_num,cycle_num)
            run_egret_file=open(input_filename,'w')
            doc.writexml(run_egret_file)
            run_egret_file.close()
       
            #you can give other user(default is public)
            follow_task_chain=task_instance.get_follow_task_chain()
            for follow_task in follow_task_chain:
                cwd=follow_task.get_cwd()
                lp_res_filename=follow_task.get_lp_res_filename()
                lp_file=os.path.join(cwd,lp_res_filename+'.LP')
                res_file=os.path.join(cwd,lp_res_filename+'.RES')
                shutil.copy(lp_file, current_workdirectory, follow_symlinks=True)
                shutil.copy(res_file, current_workdirectory, follow_symlinks=True)
        except Exception as e:
            error_message={'error_message':e}
            print(e)
            return Response(data=error_message,status=404)
        
        
        
        #begin egret calculation
        process=Popen(['runegret','-i',input_filename])
        return_code=process.wait()
        
        success_message={'task_ID':task_instance.pk,'task_name':task_name,'task_type':task_type,}
        success_message['xml_path']=xml_path
        success_message['success_message']='your request has been handled successfully'
        
        task_instance.task_status=1
        task_instance.save()
        
        if return_code is not None:
            return Response(data=success_message,status=200,headers={'cmd':3})
        
    if request.method =='PUT':
        query_params=request.query_params
        try:
            task_pk=query_params['pk']
            visibility=int(query_params['visibility'])
            task=EgretTask.objects.get(pk=task_pk)
            if task.user!=request.user:
                error_message={'error_message':"you have no permission"}
                print(error_message)
                return Response(data=error_message,status=404)
                
            task.visibility=visibility
            task.save()
            success_message={'success_message':'your request has been handled successfully'}
            return Response(data=success_message,status=200,)
        except Exception as e:
            error_message={'error_message':e}
            print(e)
            return Response(data=error_message,status=404)
            
        
        
@api_view(('POST','PUT','GET'))
@parser_classes((FileUploadParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def generate_loading_pattern(request, plantname,unit_num,cycle_num,format=None):
   
    
    try:
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
            return Response(data={'erro_message':e},status=404)
        loading_pattern.xml_file.delete()
        loading_pattern.xml_file=file
        loading_pattern.save()
        success_message={'success_message':'your request has been handled successfully'}
        return Response(data=success_message,status=200)
    
@api_view(('POST',))
@parser_classes((XMLParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def upload_loading_pattern(request, plantname,unit_num,cycle_num,format=None):
   
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get_or_create(unit=unit,cycle=cycle_num)[0]
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    
    
    if request.method == 'POST':
        name=request.query_params['name']
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
            print(nth_cycle,row,column,position_or_type)
            try:
 
                position_node=position_node_by_excel(nth_cycle,int(row),int(column),position_or_type)
            except Exception as e:
                error_message={'error':str(e)}
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

