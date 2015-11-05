from subprocess import Popen
import os
import shutil
from django.conf import settings
from django.core.files import File
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from calculation.functions import generate_egret_input,position_node_by_excel,sum_fuel_node
from calculation.serializers import EgretTaskSerializer,MultipleLoadingPatternSerializer
from tragopan.models import Plant,UnitParameter,Cycle
from calculation.models import EgretTask,MultipleLoadingPattern,EgretInputXML
from django.core.exceptions import MultipleObjectsReturned,ObjectDoesNotExist 
from xml.dom import minidom
#custom xml render
"""
Provides XML rendering support.
"""
from rest_framework import status


from rest_framework_xml.renderers import XMLRenderer


from rest_framework.parsers import FileUploadParser
from rest_framework_xml.parsers import XMLParser
from rest_framework.authentication import TokenAuthentication

        
 
 
@api_view(('POST',))
@parser_classes((FileUploadParser,XMLParser))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def generate_egret_task(request,format=None):
    if request.method == 'DELETE':
        query_params=request.query_params
        plant_name=query_params['plant']
        unit_num=query_params['unit']
        cycle_num=query_params['cycle']
        task_name=query_params['task_name']
        task_type=query_params['task_type']
        try:
            plant=Plant.objects.get(abbrEN=plant_name)
            unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
            cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
        except (Plant.DoesNotExist,UnitParameter.DoesNotExist,Cycle.DoesNotExist):
            error_message={'error_message':'the plant or unit or cycle does not exist in database!'}
            return Response(data=error_message,status=404)
        
        try:
            delete_task=EgretTask.objects.filter(task_name=task_name,task_type=task_type).get()
        except (MultipleObjectsReturned,ObjectDoesNotExist):
            error_message={'error_message':'more than one or zero egret task found'}
            return Response(data=error_message,status=404)
        delete_task.delete()    
             
        return Response(data={'sucess_message':'delete finished'},status=200)
        
     
    if request.method == 'GET':
        query_params=request.query_params
        plant_name=query_params['plant']
        unit_num=query_params['unit']
        cycle_num=query_params['cycle']
        plant=Plant.objects.get(abbrEN=plant_name)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
        task_list=EgretTask.objects.filter(user=request.user)
        if task_list is None:
            return Response(data={})
        
        serializer = EgretTaskSerializer(task_list,many=True)
        return Response(data=serializer.data)
        
    if request.method == 'POST':
        query_params=request.query_params
        data=request.data
        task_name=query_params['task_name']
        task_type=query_params['task_type']
        follow_depletion=query_params['follow_depletion']
        remark=query_params['remark']
        pk=query_params['pk']
        user=request.user
        input_file=data['file']
        print('start')
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
            print(plant_name,unit_num,cycle_num)
        except Exception:
            error_message={'error_message':'the cycle is nonexistent in database!'}
            return Response(data=error_message,status=404)
            
      
        #check if the task_name repeated
        task=EgretTask.objects.filter(task_name=task_name,user=user,loading_pattern=loading_pattern)
     
        if task:
            error_message={'error_message':'the taskname already exists'}
            return Response(data=error_message,status=404)
        else:
            try:
                
                task_instance=EgretTask.objects.create(task_name=task_name,task_type=task_type,user=user,follow_index=follow_depletion,remark=remark,egret_input_file=input_file,loading_pattern=loading_pattern)
            except Exception as e:
            
                error_message={'error_message':e}
                return Response(data=error_message,status=404)
        
        media_root=settings.MEDIA_ROOT
        plant_dir=os.path.join(media_root, plant_name)
        ibis_dir=os.path.join(plant_dir,'ibis_files')
        try:
            current_workdirectory=task_instance.get_cwd()
            #change directory to current task directory
            os.chdir(current_workdirectory)
    
            
            #loading pattern xml
            loading_pattern_chain=loading_pattern.loading_pattern_chain()
            loading_pattern_doc=sum_fuel_node(*loading_pattern_chain)
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
            egret_input_xml=EgretInputXML.objects.get(unit=unit)
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
            cycle_depl_file=task_instance.egret_input_file.name.split(sep='/')[-1]
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
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
        try:
            #you can give other user(default is public)
            follow_task_chain=task_instance.get_follow_task_chain()
            for follow_task in follow_task_chain:
                cwd=follow_task.get_cwd()
                lp_res_filename=follow_task.get_lp_res_filename()
                lp_file=os.path.join(cwd,lp_res_filename+'.LP')
                res_file=os.path.join(cwd,lp_res_filename+'.RES')
                shutil.copy(lp_file, current_workdirectory)
                shutil.copy(res_file, current_workdirectory)
        except Exception as e:
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
        #begin egret calculation
        process=Popen(['runegret','-i',input_filename])
        
        return_code=process.wait()
        workspace_dir=os.path.join(current_workdirectory,'.workspace')
        xml_path=os.path.join(workspace_dir,task_instance.get_lp_res_filename()+'.xml')
        
        print('task_finished')
        task_instance.result_path=xml_path
        task_instance.task_status=1
        task_instance.save()
        
       
        success_message={'success_message':'your request has been handled successfully','task_ID':task_instance.pk,'task_name':task_name,'task_type':task_type,}
        success_message['xml_path']=task_instance.result_path
        
        #if return_code is not None:
        
        return Response(data=success_message,status=200,headers={'cmd':3})
                             
    if request.method =='PUT':
        data=request.data
        task_name=data['task_name']
        task_type=data['task_type']
        plant_name=data['plant']
        unit_num=data['unit']
        cycle_num=data['cycle']
        follow_depletion=data['follow_depletion']
        user=request.user
        remark=data['remark']
        try:
            plant=Plant.objects.get(abbrEN=plant_name)
            unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
            cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
            #reactor_model_name=unit.reactor_model.name
            tmp_str="{}_U{}.{}.xml".format(plant_name,unit_num,str(cycle_num).zfill(3))
        except Exception:
            error_message={'error_message':'the cycle is nonexistent in database!'}
            return Response(data=error_message,status=404)

        try:
            exitent_tasks=EgretTask.objects.filter(task_name=task_name,user=user,task_type=task_type,)
        except Exception:
            error_message={'error_message':'the egret task is nonexistent in database!'}
            return Response(data=error_message,status=404)

        try:
            task_instance=exitent_tasks.get()
        except Exception:
            error_message={'error_message':'there are more than one tasks in database!'}
            return Response(data=error_message,status=404)
        
        #handle depletion case
        i=1
        depletion_lst=[]
        while 'DEPL_CASE'+'_'+str(i) in data:
            depletion_lst.append(data['DEPL_CASE'+'_'+str(i)])
            i+=1

        input_file=generate_egret_input(follow_depletion,plant_name,unit_num,cycle_num,depletion_lst)
        task_instance.cycle=cycle
        task_instance.remark=remark
        task_instance.follow_index=follow_depletion
        task_instance.task_status=0
        task_instance.save()
        media_root=settings.MEDIA_ROOT

        #remove all the previous files
        pre_rela_file_path=task_instance.egret_input_file.name
        pre_abs_file_path=os.path.join(media_root,*(pre_rela_file_path.split(sep='/')))
        print(pre_abs_file_path)
        parent_dir=os.path.dirname(pre_abs_file_path)
        os.chdir(os.path.dirname(parent_dir))
        shutil.rmtree(task_name)
       
        task_instance.egret_input_file.save(name=task_name+'.txt',content=input_file)
        input_file.close()
      
        try:
            rela_file_path=task_instance.egret_input_file.name
            abs_file_path=os.path.join(media_root,*(rela_file_path.split(sep='/')))
            os.chdir(os.path.dirname(abs_file_path))
            print(abs_file_path)
            process=Popen(['runegret','-i',abs_file_path])
        except:
            error_message={'error_message':'the process is wrong'}
            return Response(data=error_message,status=404)

        return_code=process.wait()
        #refresh the task status when process finished
        task_instance.task_status=1
        input_file_dir=os.path.join(os.path.dirname(abs_file_path),'.workspace')
        xml_path=os.path.join(input_file_dir,tmp_str)
        
        task_instance.result_path=xml_path
        task_instance.save()
        
        success_message={'success_message':'your request has been handled successfully','task_ID':task_instance.pk,'task_name':task_name,'task_type':task_type,'task_status':task_instance.task_status}
        success_message['xml_path']=task_instance.result_path
        
        if return_code is not None:
            return Response(data=success_message,status=200,headers={'cmd':3})
        
@api_view(('POST','PUT','GET'))
@parser_classes((FileUploadParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def generate_loading_pattern(request, plantname,unit_num,cycle_num,format=None):
   
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
    except plant.DoesNotExist or unit.DoesNotExist or cycle.DoesNotExist:
        
        return Response(status=status.HTTP_404_NOT_FOUND)
        
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
        mlps=MultipleLoadingPattern.objects.filter(user=request.user,cycle=cycle)
       
        if mlps is None:
            return Response(data={},status=200)
        else:
            serializer = MultipleLoadingPatternSerializer(mlps,many=True)
            return Response(data=serializer.data,status=200)
    
    if request.method == 'PUT':
        file=data['file']
        name=request.query_params['name']
        try:
            
            loading_pattern=MultipleLoadingPattern.objects.get(name=name,cycle=cycle,user=request.user,)
        except Exception as e:
            return Response(data={'erro_message':str(e)},status=404)
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

