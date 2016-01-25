from tragopan.models import OperationDailyParameter,ControlRodAssemblyStep,FuelAssemblyLoadingPattern,Cycle,UnitParameter,Plant,FuelAssemblyRepository,FuelAssemblyType,ControlRodCluster,OperationMonthlyParameter
from tragopan.serializers import FuelAssemblyLoadingPatternSerializer,PlantListSerializer,FuelAssemblyTypeSerializer,FuelAssemblyRepositorySerializer,OperationDailyParameterSerializer
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from rest_framework.parsers import FileUploadParser
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from rest_framework.authentication import TokenAuthentication
#from django.db.models import Q
@api_view(('GET',))
def plant_list(request,format=None):
    
    if request.method == 'GET':
        plants=Plant.objects.all()
        serializer=PlantListSerializer(plants,many=True)
        return Response(serializer.data)
    

    
@api_view(('GET',))
def fuel_assembly_type_list(request,format=None):
    
    if request.method == 'GET':
        try:
            fat=FuelAssemblyType.objects.all()
            serializer=FuelAssemblyTypeSerializer(fat,many=True)
            return Response(serializer.data)
        
        except Exception as e:
            print(e)
            error_message={'error_message':e}
            return Response(data=error_message,status=404)


@api_view(('GET','PUT'))
def fuel_assembly_detail(request,format=None):
    if request.method=='GET':
        try:
            plant_name=request.query_params['plant']
            unit_num=request.query_params['unit']
            cycle_num=request.query_params['cycle']
            pk=request.query_params['pk']
        
            plant=Plant.objects.get(abbrEN=plant_name)
            unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
            cycle=Cycle.objects.get(unit=unit,cycle=cycle_num)
            fuel_assembly=FuelAssemblyRepository.objects.get(pk=pk)
            
            if request.method == 'GET':
                serializer1=FuelAssemblyRepositorySerializer(fuel_assembly)
                data=serializer1.data
                if FuelAssemblyLoadingPattern.objects.filter(cycle=cycle,fuel_assembly=fuel_assembly):
                    falp=FuelAssemblyLoadingPattern.objects.get(cycle=cycle,fuel_assembly=fuel_assembly)
                    serializer2=FuelAssemblyLoadingPatternSerializer(falp)
                    data.update(serializer2.data)
                    
                return Response(data,status=200)
        except Exception as e:
            print(e)
            error_message={'error_message':e}
            return Response(data=error_message,status=404)
        
    if request.method=='PUT':
        if not request.user.is_superuser:
            error_message={'error_message':'you have no permission'}
            return Response(data=error_message,status=550)
            
        query_params=request.query_params
        try:
            pk=query_params['pk']
            remark=query_params['remark']
            fuel_assembly=FuelAssemblyRepository.objects.get(pk=pk)
            fuel_assembly.remark="{} {}:{}".format(fuel_assembly.remark,request.user,remark)
            if 'broken' in query_params:
                broken=query_params['broken']
                fuel_assembly.broken=int(broken)
                 
            if 'availability' in query_params:
                availability=query_params['availability']
                print(availability)
                fuel_assembly.availability=int(availability)
            fuel_assembly.save()
            print(fuel_assembly.availability)
            success_message={'success_message':'your request has been handled successfully'}
            return Response(data=success_message,status=200,)
        except Exception as e:
            print(e)
            error_message={'error_message':e}
            return Response(data=error_message,status=404)    
        
        

@api_view(('POST','GET'))
@parser_classes((XMLParser,FileUploadParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def operation_data(request,format=None):
    query_params=request.query_params
    data=request.data
   
    try:
        plantname=query_params['plant']
        unit_num=query_params['unit']
        cycle_num=query_params['cycle']
        operation_type=int(query_params['operation_type'])
        plant=Plant.objects.get(abbrEN=plantname)
        
        unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
        reactor_model=unit.reactor_model
       
        cycle=Cycle.objects.get_or_create(unit=unit,cycle=cycle_num)[0]
    except Exception as e:
        error_message={'error_message':e}
        print(error_message)
        return Response(data=error_message,status=404)
    
    if request.method=='GET':
        try:
            #start_date=query_params['start_date']
            #end_date=query_params['end_date']
            
            #get daily data
            if operation_type==1:
                op_daily_pr=OperationDailyParameter.objects.filter(cycle=cycle,)
                serializer=OperationDailyParameterSerializer(op_daily_pr,many=True)
                return Response(serializer.data)
            
            
            
        except Exception as e:
            error_message={'error_message':e}
            print(error_message)
            return Response(data=error_message,status=404)


    if request.method == 'POST':
        
        try:
            #upload daily data
            if operation_type==1:
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
                    
                    op=OperationDailyParameter.objects.create(cycle=cycle,date=Date,burnup=Bu,relative_power=P_rel,critical_boron_density=CB,axial_power_shift=AO)
                    for cluster in cluster_lst:
                        cra=ControlRodCluster.objects.get(reactor_model=reactor_model,cluster_name=cluster[0])
                        ControlRodAssemblyStep.objects.create(operation=op,control_rod_cluster=cra,step=cluster[1])       
                    
                success_message={'success_message':'your request has been handled successfully',}
                return Response(data=success_message,status=200)
            
            #upload monthly data
            elif operation_type==2:
                file=data['file']
                OperationMonthlyParameter.objects.create(raw_file=file,cycle=cycle)
                success_message={'success_message':'your request has been handled successfully',}
                return Response(data=success_message,status=200)
            
            else:
                error_message={'error_message':'the operation type is not supported yet'}
                print(error_message)
                return Response(data=error_message,status=404)
            
        
        except Exception as e:
            error_message={'error_message':e}
            print(error_message)
            return Response(data=error_message,status=404)   
            