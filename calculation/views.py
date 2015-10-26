from subprocess import Popen
import os
import shutil
from django.conf import settings
from django.shortcuts import render
from django.core.files import File
from rest_framework.response import Response
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from calculation.models import *
from calculation.functions import generate_egret_input
from calculation.serializers import *
from tragopan.models import ReactorModel,Plant,UnitParameter,Cycle,\
    FuelAssemblyLoadingPattern,ControlRodAssemblyLoadingPattern
    
from django.core.exceptions import MultipleObjectsReturned,ObjectDoesNotExist 
#custom xml render
"""
Provides XML rendering support.
"""
from rest_framework import status
from django.utils import six
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework_xml.renderers import XMLRenderer
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text
from rest_framework.renderers import BaseRenderer
from rest_framework.parsers import JSONParser,FileUploadParser
from rest_framework_xml.parsers import XMLParser
from rest_framework.authentication import TokenAuthentication
# Create your views here.
class CustomBaseFuelRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''
        print(data)

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        reactor_model_id=data[0]['composition'][0]['ibis']['reactor_model']
        xml.startElement("base_component ", {'basecore_ID':ReactorModel.objects.get(pk=reactor_model_id).name})

        self._to_xml(xml, data)

        xml.endElement("base_component ")
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        
        #base fuel
        for item in data:
            base_fuel_attr={}
            base_fuel_attr['fuel_id']=item['fuel_identity']
            base_fuel_attr['offset']='1' if item['offset'] else '0'
            base_fuel_attr['base_bottom']=item['base_bottom']
            base_fuel_attr['active_length']=item['composition'][0]['ibis']['active_length']
            xml.startElement('base_fuel',base_fuel_attr)
            
            
            composition_lst=item['composition']
            ratio_lst=[]
            color_lst=[]
            for i in composition_lst:
                ratio_lst.append(i['height'])
                color_lst.append(i['ibis']['ibis_name'])
                
            xml.startElement('axial_ratio',{})
            xml.characters(smart_text(' '.join(ratio_lst)))
            xml.endElement('axial_ratio' )
            
            xml.startElement('axial_color',{})
            xml.characters(smart_text(' '.join(color_lst)))
            xml.endElement('axial_color')
            
            #grid only choose the first one
            fuel_assembly_type=composition_lst[0]['ibis']['fuel_assembly_type']
            fuel_assembly_model=fuel_assembly_type['model']
            
            
            for grid in fuel_assembly_model['grids']:
                grid_attr={}
                grid_attr['hight']=grid['height']
                if grid_attr['hight']<base_fuel_attr['active_length']:
                    grid_attr['width']=grid['grid']['sleeve_height']
                    type=1 if grid['grid']['functionality']=='fix' else 2
                    xml.startElement('spacer_grid',grid_attr)
                    xml.characters(smart_text(type))
                    xml.endElement('spacer_grid')
                                
            xml.endElement('base_fuel' )
        #base control rod
        xml.startElement('base_control_rod',{'cr_id':"CR1",'spider':"0"})
        
        xml.startElement('axial_length',{})
        xml.characters(smart_text(400.0))
        xml.endElement('axial_length' )
        
        xml.startElement('axial_type',{})
        xml.characters(smart_text(1))
        xml.endElement('axial_type' )
        
        xml.endElement('base_control_rod' )
            
        

        

@api_view(('GET',))
@renderer_classes((CustomBaseFuelRenderer,))
def BaseFuel_list(request, plantname,format=None):
    """ 
    List all fuel assembly type
    """
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        #unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        
    except plant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        #serializer = UnitParameterSerializer(unit)
        base_fuels=BaseFuel.objects.all().filter(axial_composition__plant=plant)
        unique_base_fuels=[]
        for base_fuel in base_fuels:
            if base_fuel not in unique_base_fuels:
                unique_base_fuels.append(base_fuel)
        print(unique_base_fuels)
        serializer = CustomBaseFuelSerializer(unique_base_fuels,many=True)
        return Response(serializer.data)





class CustomBaseCoreRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''
        print(data)

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        reactor_model=ReactorModel.objects.get(pk=data['reactor_model'])
        plant=Plant.objects.get(pk=data['plant'])
        unit=UnitParameter.objects.get(plant=plant,unit=data['unit'])
        xml.startElement("basecore ", {'ID':reactor_model.name,'core_type':reactor_model.reactor_type})
        reactor_positions=reactor_model.positions.all()
        print(reactor_positions)
        num_side_asms=0
        for reactor_position in reactor_positions:
            if reactor_position.row>num_side_asms:
                num_side_asms=reactor_position.row
        #core_geo
        xml.startElement('core_geo',{'num_side_asms':str(num_side_asms)})
        
        
        xml.startElement('fuel_pitch',{})
        xml.characters(smart_text(reactor_model.fuel_pitch))
        xml.endElement('fuel_pitch')
        
        xml.startElement('std_fuel_len',{})
        xml.characters(smart_text(reactor_model.active_height))
        xml.endElement('std_fuel_len')   
        
        xml.startElement('fuel_map',{})
        fuel_map_lst=[]
        for i in range(1,num_side_asms+1):
            for j in range(1,num_side_asms+1):
                fuel_position=reactor_model.positions.filter(row=i,column=j)
                if fuel_position:
                    fuel_map_lst.append('1')
                else:
                    fuel_map_lst.append('0')
        
        xml.characters(smart_text(' '.join(fuel_map_lst)))
        xml.endElement('fuel_map')
        
        xml.endElement('core_geo')   
        
        #control rod map
        xml.startElement('rcca',{})
        control_rod_assembly_lst=[]
        bank_id_lst=[]
        
        for position in reactor_positions:
            try:
                cralp=ControlRodAssemblyLoadingPattern.objects.filter(reactor_position=position).get(cycle__unit=unit)
                control_rod_assembly_lst.append(cralp.control_rod_assembly.cluster_name)
                if cralp.control_rod_assembly.cluster_name not in bank_id_lst:
                    bank_id_lst.append(cralp.control_rod_assembly.cluster_name)
            except Exception:
                control_rod_assembly_lst.append('0')
         
        index=1       
        for name in bank_id_lst:
            xml.startElement('bank_id',{'basez':"9.5875",'index':str(index)})
            index+=1
            xml.characters(smart_text(name))
            xml.endElement('bank_id') 
            
        xml.startElement('map',{})    
        xml.characters(smart_text(' '.join(control_rod_assembly_lst)))
        xml.endElement('map') 
        
        xml.startElement('step_size',{})    
        xml.characters(smart_text(1.5832))
        xml.endElement('step_size') 

        xml.endElement('rcca') 
        
        #reflector
        xml.startElement('reflector',{})    
        
        xml.startElement('bot_br',{})
        xml.characters(smart_text('BR_BOT'))    
        xml.endElement('bot_br') 
        
        xml.startElement('top_br',{})
        xml.characters(smart_text('''
        BR_TOP
        BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP
        BR_TOP BR_TOP BR_TOP'''))    
        xml.endElement('top_br')
        
        xml.startElement('radial_br',{'index':'1'})
        xml.characters(smart_text('BR3  BR3  BR3  BR9  BR6  BR5  BR7  BR3  BR3  BR9  BR6  BR5  BR7  BR9 '))    
        xml.endElement('radial_br') 
        
        xml.startElement('radial_br',{'index':'2'})
        xml.characters(smart_text('BR4  BR4  BR4 BR10 BR12 BR11  BR8  BR4  BR4 BR10 BR12 BR11  BR8 BR10 BR12'))    
        xml.endElement('radial_br') 
        
        xml.endElement('reflector') 
        

        

        xml.endElement("basecore ")
        xml.endDocument()
        return stream.getvalue()

    

@api_view(('GET','POST'))
@renderer_classes((CustomBaseCoreRenderer,))    
def BaseCore_detail(request, plantname,unit_num,format=None):
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        
    except plant.DoesNotExist or unit.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UnitParameterSerializer(unit)
        return Response(serializer.data)
    
    if request.method == 'POST':
        data=request.data
        return Response(data)
  
  
  
  
class CustomLoadingPatternRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''
        print(data)

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        
        unit=UnitParameter.objects.get(pk=data[0]['unit'])
        plant=unit.plant
        reactor_model=unit.reactor_model
        reactor_positions=reactor_model.positions.all()
        cycles=unit.cycles.all()
        #fuel_assembly_model=FuelAssemblyLoadingPattern.objects.get(pk=data[0]['fuel_assembly_loading_patterns'][0]).fuel_assembly.type.model
        
        xml.startElement("loading_pattern ", {'basecore_ID':reactor_model.name,'core_id':reactor_model.name+'_U'+str(unit.unit)})
        
        
        for cycle in cycles:
            
            control_rod_assembly_loading_patterns=cycle.control_rod_assembly_loading_patterns.all()
            if control_rod_assembly_loading_patterns:
                xml.startElement('control_rod', {'cycle':str(cycle.cycle)})
                
                xml.startElement('map', {})
                cra_position_lst=[]
                for reactor_position in reactor_positions:
                    cra_pattern=control_rod_assembly_loading_patterns.filter(reactor_position=reactor_position)
                    if cra_pattern:
                        cra=cra_pattern.get().control_rod_assembly
                        cra_position_lst.append('CR1')
                    else:
                        cra_position_lst.append('0')
                xml.characters(smart_text(' '.join(cra_position_lst)))    
                        
                xml.endElement('map')
                
                xml.endElement('control_rod')
        
        for cycle in cycles: 
            #fuel_assembly_loading_patterns=cycle.fuel_assembly_loading_patterns.all()
            #burnable_posison_assembly_positions=cycle.burnable_posison_assembly_positions.all()
           
            fuel_lst=[]
            previous_cycle_lst=[]
                     
            for reactor_position in reactor_positions:
                fuel_assembly_loading_pattern=cycle.fuel_assembly_loading_patterns.filter(reactor_position=reactor_position).get()
                burnable_poison_assembly_position=cycle.bpa_loading_patterns.filter(reactor_position=reactor_position)
                fuel_assembly_type=fuel_assembly_loading_pattern.fuel_assembly.type
                if fuel_assembly_loading_pattern.get_previous():
                    [previous_cycle,previous_position_row,previous_position_column]=fuel_assembly_loading_pattern.get_previous().split('-')
                    position='{}{}'.format(previous_position_row.zfill(2), previous_position_column.zfill(2))
                    fuel_lst.append(position)
                    if previous_cycle!=cycle.cycle-1:
                        
                        previous_cycle_lst.append([previous_cycle,reactor_position.row,reactor_position.column])
                       
                        
                else:
                    if burnable_poison_assembly_position:
                        ibis=Ibis.objects.filter(fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=burnable_poison_assembly_position.get().burnable_poison_assembly).get()
                        base_fuel=ibis.base_fuel_compositions.get()
                        fuel_lst.append(base_fuel.base_fuel.fuel_identity)
                    else:
                        ibis=Ibis.objects.filter(fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=None).get()
                        base_fuels=ibis.base_fuel_compositions.all()     
                        for base_fuel in base_fuels:
                            if not base_fuel.base_fuel.if_insert_burnable_fuel():
                                fuel_lst.append(base_fuel.base_fuel.fuel_identity)
                            
            print(len(fuel_lst))    
                           
            xml.startElement('fuel', {'cycle':str(cycle.cycle)})
                
            
            xml.startElement('map', {})
            xml.characters(smart_text(' '.join(fuel_lst)))      
            xml.endElement('map')
            
            for previous_cycle_info in previous_cycle_lst:
                if int(previous_cycle_info[0])!=cycle.cycle-1:
                    xml.startElement('cycle', {'row':str(previous_cycle_info[1]),'col':str(previous_cycle_info[2])})
                    xml.characters(smart_text(previous_cycle_info[0]))      
                    xml.endElement('cycle')
                            
            xml.endElement('fuel')
            
        xml.endElement("loading_pattern ")
        xml.endDocument()
        return stream.getvalue() 
  
    
@api_view(('GET','POST'))
@renderer_classes((CustomLoadingPatternRenderer,))      
def LoadingPattern_list(request, plantname,unit_num,format=None):
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=unit.cycles.all()
    except plant.DoesNotExist or unit.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CycleSerializer(cycle,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        data=request.data
        print(data)
        
 
 
@api_view(('GET','POST','PUT','DELETE'))
@parser_classes((XMLParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def generate_egret_task(request,format=None):
    if request.method == 'DELETE':
        data=request.GET
        plant_name=data['plant']
        unit_num=data['unit']
        cycle_num=data['cycle']
        task_name=data['task_name']
        task_type=data['task_type']
        try:
            plant=Plant.objects.get(abbrEN=plant_name)
            unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
            cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
        except (Plant.DoesNotExist,UnitParameter.DoesNotExist,Cycle.DoesNotExist):
            error_message={'error_message':'the plant or unit or cycle does not exist in database!'}
            return Response(data=error_message,status=404)
        
        try:
            delete_task=EgretTask.objects.filter(cycle=cycle,task_name=task_name,task_type=task_type).get()
        except (MultipleObjectsReturned,ObjectDoesNotExist):
            error_message={'error_message':'more than one or zero egret task found'}
            return Response(data=error_message,status=404)
        delete_task.delete()    
             
        return Response(data={'sucess_message':'delete finished'},status=200)
        
     
    if request.method == 'GET':
        data=request.GET
        plant_name=data['plant']
        unit_num=data['unit']
        cycle_num=data['cycle']
        plant=Plant.objects.get(abbrEN=plant_name)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
        task_list=EgretTask.objects.filter(user=request.user,cycle=cycle)
        if task_list is None:
            return Response(data={})
        
        serializer = EgretTaskSerializer(task_list,many=True)
        return Response(data=serializer.data)
        
    if request.method == 'POST':
        data=request.data
        task_name=data['task_name']
        task_type=data['task_type']
        plant_name=data['plant']
        unit_num=data['unit']
        cycle_num=data['cycle']
        follow_depletion=data['follow_depletion']
        remark=data['remark']
        user=request.user
        try:
            plant=Plant.objects.get(abbrEN=plant_name)
            unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
            cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
            #reactor_model_name=unit.reactor_model.name
            tmp_str="{}_U{}.{}.xml".format(plant_name,unit_num,str(cycle_num).zfill(3))
        except Exception:
            error_message={'error_message':'the cycle is nonexistent in database!'}
            return Response(data=error_message,status=404)
            
        #handle depletion case
        i=1
        depletion_lst=[]
        while 'DEPL_CASE'+'_'+str(i) in data:
            depletion_lst.append(data['DEPL_CASE'+'_'+str(i)])
            i+=1
        
        input_file=generate_egret_input(follow_depletion,plant_name,unit_num,cycle_num,depletion_lst)
      
        #check if the task_name repeated
        task=EgretTask.objects.filter(task_name=task_name,user=user,cycle=cycle)
        print(task)
        if task:
            error_message={'error_message':'the taskname already exists'}
            return Response(data=error_message,status=404)
        else:
            
            print(task_name,task_type,user,cycle,follow_depletion,remark)
            task_instance=EgretTask.objects.create(task_name=task_name,task_type=task_type,user=user,cycle=cycle,follow_index=follow_depletion,remark=remark)
            task_instance.egret_input_file.save(name=task_name+'.txt',content=input_file)
            input_file.close()
        
        print(task_instance)
        media_root=settings.MEDIA_ROOT
        try:
            rela_file_path=task_instance.egret_input_file.name
            abs_file_path=os.path.join(media_root,*(rela_file_path.split(sep='/')))
            os.chdir(os.path.dirname(abs_file_path))
            for i in range(1,cycle_num):
                cycle_follow_dir=os.path.join(os.path.dirname(os.path.dirname(abs_file_path)).replace('cycle%d'%cycle_num,'cycle%d'%i),'follow')
                print(cycle_follow_dir)
                filenames=os.listdir(cycle_follow_dir)
                print(filenames)
                for filename in filenames:
                    if filename.endswith('.LP'):
                        lp_file=os.path.join(cycle_follow_dir,filename)
                        link_process=Popen(['ln','-sf',lp_file,'.'])
                        link_process.wait()
             
            print(abs_file_path)   
            process=Popen(['runegret','-i',abs_file_path])
        except:
            error_message={'error_message':'the process is wrong'}
            return Response(data=error_message,status=404)

        return_code=process.wait()
        input_file_dir=os.path.join(os.path.dirname(abs_file_path),'.workspace')
        xml_path=os.path.join(input_file_dir,tmp_str)
        
        print('task_finished')
        task_instance.result_path=xml_path
        task_instance.task_status=1
        task_instance.save()
       
        success_message={'success_message':'your request has been handled successfully','task_ID':task_instance.pk,'task_name':task_name,'task_type':task_type,'task_status':task_instance.task_status}
        success_message['xml_path']=task_instance.result_path
        
        if return_code is not None:
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
            exitent_tasks=EgretTask.objects.filter(task_name=task_name,cycle=cycle,user=user,task_type=task_type,)
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
        print('1')
        return Response(status=status.HTTP_404_NOT_FOUND)
        
    data=request.data
    print(data)
    if request.method == 'POST':
        file=data['file']
        name=request.query_params['name']
        try:
            pre_pk=request.query_params['pre_pk']
            print(pre_pk)
            pre_loading_pattern=MultipleLoadingPattern.objects.get(pk=pre_pk)
            mlp=MultipleLoadingPattern(user=request.user,name=name,xml_file=file,cycle=cycle,pre_loading_pattern=pre_loading_pattern)
        except:
            mlp=MultipleLoadingPattern(user=request.user,name=name,xml_file=file,cycle=cycle)
        mlp.save()
        success_message={'success_message':'your request has been handled successfully','pk':mlp.pk}
        return Response(data=success_message,status=200)
    
    if request.method=='GET':
        mlps=MultipleLoadingPattern.objects.filter(user=request.user,cycle=cycle)
        print(mlps)
        if mlps is None:
            return Response(data={},status=200)
        else:
            serializer = MultipleLoadingPatternSerializer(mlps,many=True)
            return Response(data=serializer.data,status=200)

