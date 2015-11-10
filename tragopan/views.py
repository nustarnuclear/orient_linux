from __future__ import unicode_literals
from tragopan.models import OperationParameter,ControlRodAssemblyStep,FuelAssemblyLoadingPattern,Cycle,ReactorPosition,UnitParameter,\
Plant,FuelAssemblyRepository,FuelAssemblyType,ControlRodAssembly

from tragopan.serializers import FuelAssemblyLoadingPatternSerializer,CycleSerializer,PlantListSerializer,FuelAssemblyTypeSerializer\
,FuelAssemblyRepositorySerializer,FuelAssemblyLoadingPatternSerializer1

from django.db.models import Max
from rest_framework.response import Response
from rest_framework import status
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from rest_framework.authentication import TokenAuthentication

#custom xml render
"""
Provides XML rendering support.
"""

from django.utils import six
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six import StringIO
from django.utils.encoding import smart_text
from rest_framework.renderers import BaseRenderer

class CustomXMLRenderer(BaseRenderer):
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

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement("orient", {'test':'test'})

        self._to_xml(xml, data)

        xml.endElement("orient")
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement(self.item_tag_name, {})
                self._to_xml(xml, item)
                xml.endElement(self.item_tag_name)

        elif isinstance(data, dict):
            for key, value in six.iteritems(data):
                try:
            
                    tmp_lst=value.split(sep='~')
                    attr_dic={}
                    for i in range(1,len(tmp_lst)):
                        if i %2 != 0:
                            attr_dic[tmp_lst[i]]=tmp_lst[i+1]
                            
                    xml.startElement(key, attr_dic)
                    self._to_xml(xml, tmp_lst[0])
                    xml.endElement(key)
                except AttributeError:
                    xml.startElement(key, {})
                    self._to_xml(xml, value)
                    xml.endElement(key)
                

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))




       
    
    
@api_view(['GET', 'POST'])
def fuel_assembly_loading_pattern_list(request,format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        fuel_assembly_loading_patterns = FuelAssemblyLoadingPattern.objects.all()
        serializer = FuelAssemblyLoadingPatternSerializer(fuel_assembly_loading_patterns, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FuelAssemblyLoadingPatternSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
   
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def fuel_assembly_loading_pattern_detail(request, pk,format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        fuel_assembly_loading_pattern = FuelAssemblyLoadingPattern.objects.get(pk=pk)
    except FuelAssemblyLoadingPattern.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FuelAssemblyLoadingPatternSerializer(fuel_assembly_loading_pattern)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FuelAssemblyLoadingPatternSerializer(fuel_assembly_loading_pattern, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        fuel_assembly_loading_pattern.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET', 'POST'])
def cycle_list(request,format=None):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        cycles = Cycle.objects.all()
        serializer = CycleSerializer(cycles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CycleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
   
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
 
    
@api_view(('GET','POST','PUT','DELETE'))
@renderer_classes((CustomXMLRenderer,))
def cycle_detail(request, plantname,unit_num,cycle_num,format=None):
    
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        unit=UnitParameter.objects.get(plant=plant,unit=int(unit_num))
    
    except Plant.DoesNotExist or UnitParameter.DoesNotExist:
        error_message={'error_message':'the plant or unit does not exist in database!'}
        return Response(data=error_message,status=404)
    
  
    
    if request.method == 'DELETE':
        c=Cycle.objects.filter(unit=unit).aggregate(Max('cycle'))
        cmax=c['cycle__max']
        print(cmax)
        if int(cycle_num)==cmax:
            success_message={'success_message':'sucessful'}
            return Response(data=success_message,status=200)
        else:
            error_message={'error_message':'you can only delete the last cycle of certain unit'}
            return Response(data=error_message,status=404)
            
   
    if request.method == 'POST':
        
        if int(cycle_num)<13:
            return Response(data={'error_message':'you have no permission'},status=404)
        
        print(cycle_num)
        cycle = Cycle.objects.get_or_create(unit=unit,cycle=int(cycle_num))[0]
        print(cycle)    
        reactor_model=unit.reactor_model
        reactor_position_objs=ReactorPosition.objects.filter(reactor_model=reactor_model,)
        data=request.data
        print(data)
        fuel_assembly_loading_patterns=data['fuel_assembly_loading_patterns']
        print(len(fuel_assembly_loading_patterns))
        created_num,updated_num=0,0
        for fuel_assembly_loading_pattern in fuel_assembly_loading_patterns:
            reactor_position=fuel_assembly_loading_pattern['reactor_position']
            row=reactor_position['row']
            column=reactor_position['column']
            reactor_position_obj=reactor_position_objs.get(row=row,column=column)
            previous=fuel_assembly_loading_pattern['get_previous']
            
            fuel_id=fuel_assembly_loading_pattern['fuel_assembly']
            # if not fresh
            if previous:
                fuel_assembly=FuelAssemblyRepository.objects.get(pk=fuel_id)
                
            else:
                fuel_assembly_type=FuelAssemblyType.objects.get(pk=fuel_id)
                fuel_assembly=FuelAssemblyRepository.objects.create(type=fuel_assembly_type,plant=plant)
            try:
                exist_pattern=FuelAssemblyLoadingPattern.objects.get(cycle=cycle,reactor_position=reactor_position_obj)
                if exist_pattern.fuel_assembly!=fuel_assembly:
                    exist_pattern.fuel_assembly=fuel_assembly
                    exist_pattern.save()
                    updated_num +=1
            except Exception:
                new_pattern=FuelAssemblyLoadingPattern.objects.create(cycle=cycle,reactor_position=reactor_position_obj,fuel_assembly=fuel_assembly)
                created_num +=1
            
        sucess_message={'created':created_num,'updated':updated_num}       
        return Response(data=sucess_message,status=200)
    
    
   

    if request.method == 'GET':
        try:
            cycle = Cycle.objects.get(unit=unit,cycle=cycle_num)
        except Cycle.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CycleSerializer(cycle)
        return Response(serializer.data)
    


@api_view(('GET',))
def plant_list(request,format=None):
    
    if request.method == 'GET':
        plants=Plant.objects.all()
        serializer=PlantListSerializer(plants,many=True)
        return Response(serializer.data)
    

    
@api_view(('GET',))
def fuel_assembly_type_list(request,format=None):
    
    if request.method == 'GET':
        fat=FuelAssemblyType.objects.all()
        serializer=FuelAssemblyTypeSerializer(fat,many=True)
        return Response(serializer.data)


@api_view(('GET',))
def fuel_assembly_detail(request,format=None):
    
    plant_name=request.query_params['plant_name']
    unit_num=request.query_params['unit_num']
    cycle_num=request.query_params['cycle_num']
    pk=request.query_params['pk']
    try:
        plant=Plant.objects.get(abbrEN=plant_name)
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
        fuel_assembly=FuelAssemblyRepository.objects.get(pk=pk)
        falp=FuelAssemblyLoadingPattern.objects.get(cycle=cycle,fuel_assembly=fuel_assembly)
        if request.method == 'GET':
            serializer1=FuelAssemblyRepositorySerializer(fuel_assembly)
            
            serializer2=FuelAssemblyLoadingPatternSerializer1(falp)
            data=serializer1.data
            data.update(serializer2.data)
            return Response(data)
    except Exception as e:
        print(e)
        error_message={'error_message':e}
        return Response(data=error_message,status=404)
        

@api_view(('POST',))
@parser_classes((XMLParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def upload_operation_data(request,format=None):
   
    plantname=request.query_params['plant']
    unit_num=request.query_params['unit']
    cycle_num=request.query_params['cycle']
   
    try:
        plant=Plant.objects.get(abbrEN=plantname)
        
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        reactor_model=unit.reactor_model
       
        cycle=Cycle.objects.get_or_create(unit=unit,cycle=cycle_num)[0]
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


    if request.method == 'POST':
        data=request.data
        for item in data:
            cluster_lst=[]
            for key,value in item.items():
                if key.startswith('CRD'):
                    cluster_lst.append([key.split(sep='_')[-1],value])
            
            Bu=item['Bu']
            AO=item['AO']
            CB=item['CB']
            P_rel=item['P_rel']
            Date=item['Date']
            
            op=OperationParameter.objects.create(cycle=cycle,date=Date,burnup=Bu,relative_power=P_rel,critical_boron_density=CB,axial_power_shift=AO)
            for cluster in cluster_lst:
                cra=ControlRodAssembly.objects.get(reactor_model=reactor_model,cluster_name=cluster[0])
                cras=ControlRodAssemblyStep.objects.create(operation=op,control_rod_assembly=cra,step=cluster[1])       
            
        success_message={'success_message':'your request has been handled successfully',}
        return Response(data=success_message,status=200)