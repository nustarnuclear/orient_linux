from rest_framework import serializers
from tragopan.models import Element,ReactorPosition,FuelAssemblyLoadingPattern,Plant,UnitParameter,BurnablePoisonAssembly,BurnablePoisonAssemblyLoadingPattern,\
ControlRodAssembly,ControlRodAssemblyLoadingPattern,Grid,GridPosition,FuelAssemblyType,Cycle,FuelAssemblyModel,FuelAssemblyRepository,ControlRodCluster,OperationDailyParameter

class ElementSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Element
        fields = ('atomic_number', 'symbol', 'nameCH', 'nameEN', 'reference', )
        
        
class ReactorPositionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReactorPosition
        fields = ( 'row','column', )
  

        
class PlantSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  Plant
        fields = ( 'abbrEN',)       
        
class UnitParameterSerializer(serializers.ModelSerializer):
    plant=PlantSerializer()
    class Meta:
        model = UnitParameter
        fields = ( 'plant','unit')
        
class BurnablePoisonAssemblySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BurnablePoisonAssembly
        fields = ( 'get_poison_rod_num','get_poison_rod_height',)
   
class BurnablePoisonAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    reactor_position=ReactorPositionSerializer()
    burnable_poison_assembly=BurnablePoisonAssemblySerializer()
    class Meta:
        model = BurnablePoisonAssemblyLoadingPattern
        fields = ( 'reactor_position','burnable_poison_assembly')
        
        
class ControlRodClusterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ControlRodCluster
        fields = ( 'cluster_name',) 
        
class ControlRodAssemblySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ControlRodAssembly
        fields = ( 'cluster','pk')        

class ControlRodAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    reactor_position=ReactorPositionSerializer()
    control_rod_assembly=ControlRodAssemblySerializer()
    
    class Meta:
        model = ControlRodAssemblyLoadingPattern
        fields = ( 'reactor_position','control_rod_assembly')       


        

class GridListingField(serializers.RelatedField):
    
    def to_representation(self, value):
        
        return "{}~width~{}".format(value.functionality ,value.sleeve_height)

        

class GridSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Grid
        fields = ( 'side_length','sleeve_height','functionality')   
        
class GridPositionSerializer(serializers.ModelSerializer):
    grid=GridListingField(read_only=True,)
    class Meta:
        model = GridPosition
        fields = ( 'height','grid')

class GridPositionListingField(serializers.RelatedField):
    
    def to_representation(self, value):
        
        return "{}~hight~{}~width~{}".format(value.grid.functionality, value.height,value.grid.sleeve_height)
         
        
class FuelAssemblyModelSerializer(serializers.ModelSerializer): 
     
    grids=GridPositionSerializer(many=True, read_only=True)
    
    class Meta:
        model = FuelAssemblyModel
        fields = ( 'name','overall_length','grids',)     
        
        
class BaseFuelAssemblySerializer(serializers.ModelSerializer):
    model=FuelAssemblyModelSerializer()
    
    class Meta:
        model = FuelAssemblyType
        fields = ( 'assembly_enrichment','model','name')


        
################################################# 
class CycleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = ( 'cycle',)
        
class UnitParameterListSerializer(serializers.ModelSerializer):
    cycles=CycleListSerializer(many=True, read_only=True)
    class Meta:
        model = UnitParameter
        fields = ( 'unit','cycles')

 
   
class PlantListSerializer(serializers.ModelSerializer):
    units=UnitParameterListSerializer(many=True, read_only=True)
    class Meta:
        model =  Plant
        fields = ( 'abbrEN','units')
        
class FuelAssemblyTypeSerializer(serializers.ModelSerializer):
    model=FuelAssemblyModelSerializer()
    class Meta:
        model =  FuelAssemblyType
        fields = ( 'pk','assembly_enrichment','model','assembly_name')   
        

class FuelAssemblyRepositorySerializer(serializers.ModelSerializer):
    type=FuelAssemblyTypeSerializer()
    class Meta:
        model = FuelAssemblyRepository
        fields = ( 'type','remark','broken','availability')  
        
class FuelAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FuelAssemblyLoadingPattern
        fields = ( 'get_all_previous','if_insert_bpa','if_insert_cra')  
        
class OperationDailyParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationDailyParameter
        depth=1
        exclude = ('time_inserted','last_modified','remark')
        
    
    
        