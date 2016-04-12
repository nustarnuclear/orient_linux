from rest_framework import serializers
from tragopan.models import FuelAssemblyType,FuelAssemblyModel,Grid,GridPosition,UnitParameter,Cycle,BurnablePoisonAssembly
from calculation.models import EgretTask,MultipleLoadingPattern,PreRobinInput
from django.contrib.auth.models import User,Group

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

class FuelAssemblyModelSerializer(serializers.ModelSerializer):
    grid_positions=GridPositionSerializer(many=True, read_only=True)
    class Meta:
        model=FuelAssemblyModel
        fields=('pk','name','active_length','grid_positions')

class FuelAssemblyTypeSerializer(serializers.ModelSerializer):
    model=FuelAssemblyModelSerializer()
    class Meta:
        model=FuelAssemblyType
        fields=('pk','model','assembly_enrichment')
        
class UnitParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model=UnitParameter
        fields=('plant','unit','reactor_model')
        
        
class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = ( 'unit','fuel_assembly_loading_patterns')
 
 
class EgretCycleSerializer(serializers.ModelSerializer):
    unit=UnitParameterSerializer()
    class Meta:
        model = Cycle
        fields = ( 'unit','cycle')
        
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields=('name','user_set')

        
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields=('username',)
           
               
class EgretTaskSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    #result_path=serializers.FilePathField(path='')
    class Meta:
        model = EgretTask
        fields = ( 'pk','task_name','task_type','egret_input_file','task_status','remark','user','pre_egret_task','visibility','authorized','start_time','end_time','recalculation_depth','get_input_filename','result_file')       
   
class MultipleLoadingPatternSerializer(serializers.ModelSerializer): 
    cycle=EgretCycleSerializer()
    user=UserSerializer()
    class Meta:
        model = MultipleLoadingPattern
        fields = ( 'pk','name','cycle','xml_file','user','pre_loading_pattern','visibility','authorized')
        
class BurnablePoisonAssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model=BurnablePoisonAssembly
        fields=('pk','bp_num','bottom_height')

class PreRobinInputSerializer(serializers.ModelSerializer):
    fuel_assembly_type=FuelAssemblyTypeSerializer()
    burnable_poison_assembly=BurnablePoisonAssemblySerializer()
    unit=UnitParameterSerializer()
    class Meta:
        model=PreRobinInput
        fields = ( 'pk','unit','fuel_assembly_type','burnable_poison_assembly',)