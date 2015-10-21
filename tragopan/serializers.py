from rest_framework import serializers
from tragopan.models import *
from calculation.models import *

class ElementSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Element
        fields = ('atomic_number', 'symbol', 'nameCH', 'nameEN', 'reference', )
        
        
class ReactorPositionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReactorPosition
        fields = ( 'row','column', )

class FuelAssemblyListingField(serializers.RelatedField):
    def to_representation(self, value):
        
        first_loading_pattern=FuelAssemblyLoadingPattern.objects.filter(fuel_assembly=value).first()
        first_cycle=first_loading_pattern.cycle.cycle
        first_position=first_loading_pattern.reactor_position
        
        return "{}~type~{}~enrichment~{}~first_cycle~{}~row~{}~column~{}".format(value.pk, value.type.pk,value.type.assembly_enrichment,first_cycle,first_position.row,first_position.column)

class FuelAssemblyRepositorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FuelAssemblyRepository
        fields = ( 'id','type', )
               
        
class FuelAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    reactor_position=ReactorPositionSerializer()
    fuel_assembly=FuelAssemblyListingField(read_only=True)
    #previous_reactor_position=serializers.PrimaryKeyRelatedField(query_set=FuelAssemblyLoadingPattern.objects.filter(fuel_assembly=fuel_assembly))
    
    class Meta:
        model = FuelAssemblyLoadingPattern
        fields = ( 'reactor_position','fuel_assembly', 'get_previous',)
        
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
        

class ControlRodAssemblySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ControlRodAssembly
        fields = ( 'cluster_name',)        

class ControlRodAssemblyLoadingPatternSerializer(serializers.ModelSerializer):
    reactor_position=ReactorPositionSerializer()
    control_rod_assembly=ControlRodAssemblySerializer()
    
    class Meta:
        model = ControlRodAssemblyLoadingPattern
        fields = ( 'reactor_position','control_rod_assembly')       

class CycleSerializer(serializers.ModelSerializer):
    #unit=UnitParameterSerializer()
    fuel_assembly_loading_patterns=FuelAssemblyLoadingPatternSerializer(many=True, read_only=True)
    bpa_loading_patterns=BurnablePoisonAssemblyLoadingPatternSerializer(many=True, read_only=True)
    control_rod_assembly_loading_patterns=ControlRodAssemblyLoadingPatternSerializer(many=True, read_only=True)
    class Meta:
        model = Cycle
        fields = ( 'fuel_assembly_loading_patterns','bpa_loading_patterns','control_rod_assembly_loading_patterns')
        

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
        fields = ( 'assembly_enrichment','model',)


        
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
        
        
        