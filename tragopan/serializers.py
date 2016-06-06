from rest_framework import serializers
from tragopan.models import ReactorPosition,FuelAssemblyLoadingPattern,Plant,UnitParameter,BurnablePoisonAssembly,\
Grid,GridPosition,FuelAssemblyType,Cycle,FuelAssemblyModel,FuelAssemblyRepository,ControlRodCluster,OperationDailyParameter,ControlRodAssemblyStep,FuelAssemblyPosition,\
OperationMonthlyParameter,OperationBankPosition,OperationDistributionData
     
class ReactorPositionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReactorPosition
        fields = ( 'row','column', )
        
class PlantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Plant
        fields = ( 'abbrEN','pk','abbrCH')       
        
class UnitParameterSerializer(serializers.ModelSerializer):
    plant=PlantSerializer()
    class Meta:
        model = UnitParameter
        fields = ( 'plant','unit')
        
class BurnablePoisonAssemblySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BurnablePoisonAssembly
        fields = ( 'get_poison_rod_num','get_poison_rod_height',)
   

         
class ControlRodClusterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ControlRodCluster
        fields = ( 'cluster_name',) 
        

    
class FuelAssemblyModelSerializer(serializers.ModelSerializer): 
    class Meta:
        model = FuelAssemblyModel
        fields = ( 'name','active_length',)     
        

class GridSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grid
        fields = ('sleeve_height','functionality','sleeve_material')   
        depth=1
        
class GridPositionSerializer(serializers.ModelSerializer):
    grid=GridSerializer()
    class Meta:
        model = GridPosition
        fields = ( 'height','grid')
class FuelAssemblyPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model=FuelAssemblyPosition
        fields = ( 'row','column','type')

class FuelAssemblyModelPlusSerializer(serializers.ModelSerializer):
    grid_positions=GridPositionSerializer(many=True, read_only=True)
    positions=FuelAssemblyPositionSerializer(many=True, read_only=True)
    class Meta:
        model=FuelAssemblyModel
        fields=('pk','name','active_length','grid_positions','positions')
        
################################################# 
class CycleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = ( 'cycle',)
        
class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = ('unit' ,'cycle',)
class UnitParameterListSerializer(serializers.ModelSerializer):
    cycles=CycleListSerializer(many=True, read_only=True)
    class Meta:
        model = UnitParameter
        fields = ( 'pk','unit','cycles')

 
   
class PlantListSerializer(serializers.ModelSerializer):
    units=UnitParameterListSerializer(many=True, read_only=True)
    class Meta:
        model =  Plant
        fields = ( 'abbrEN','units','pk','abbrCH')
        
class FuelAssemblyTypeSerializer(serializers.ModelSerializer):
    model=FuelAssemblyModelSerializer()
    class Meta:
        model =  FuelAssemblyType
        fields = ( 'pk','assembly_enrichment','model','assembly_name')   
        

class FuelAssemblyRepositorySerializer(serializers.ModelSerializer):
    type=FuelAssemblyTypeSerializer()
    class Meta:
        model = FuelAssemblyRepository
        fields = ( 'id','type','remark','broken','availability','broken_cycle_num','unavailable_cycle_num')  
        
class FuelAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FuelAssemblyLoadingPattern
        fields = ( 'get_all_previous','if_insert_bpa','if_insert_cra')  
class ControlRodAssemblyStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlRodAssemblyStep
        fields = ('cluster_name','step')
            
class OperationDailyParameterSerializer(serializers.ModelSerializer):
    control_rods=ControlRodAssemblyStepSerializer(many=True, read_only=True)
    class Meta:
        model = OperationDailyParameter
        exclude = ('time_inserted','last_modified','remark')       


class OperationBankPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationBankPosition
        fields = ('cluster_name','step')
        
class OperationDistributionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationDistributionData
        fields = ('position','relative_power','FDH','axial_power_offset')
        
class OperationMonthlyParameterSerializer(serializers.ModelSerializer):
    cluster_steps=OperationBankPositionSerializer(many=True, read_only=True)
    distribution_data=OperationDistributionDataSerializer(many=True, read_only=True)
    class Meta:
        model = OperationMonthlyParameter
        exclude = ('time_inserted','last_modified','remark','raw_file','bank_position','distribution')       
        
        