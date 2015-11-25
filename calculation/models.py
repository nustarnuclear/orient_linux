from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
from tragopan.models import FuelAssemblyType, BurnablePoisonAssembly,\
    FuelAssemblyRepository, FuelAssemblyLoadingPattern
from django.conf import settings
import os
from xml.dom import minidom 
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Create your models here.

def get_ibis_upload_path(instance,filename):
    plant_name=instance.plant.abbrEN
    
    return "{}/ibis_files/{}".format(plant_name,filename)

def get_robin_upload_path(instance,filename):
    plant_name=instance.plant.abbrEN
    file_type=instance.file_type
    assembly_name=instance.fuel_assembly_type.model.name
    enrichment=instance.fuel_assembly_type.assembly_enrichment
    
    if instance.burnable_poison_assembly:
        str_num=str(instance.burnable_poison_assembly.rod_positions.count())
    else:
        str_num='00'
        
    tmp=str(int(enrichment*1000))+str_num
    
    return "{}/robin_files/{}/{}/{}/{}".format(plant_name,file_type,assembly_name,tmp,filename)

def get_pre_robin_upload_path(instance,filename):
    plant_name=instance.plant.abbrEN
    file_type=instance.file_type
    assembly_name=instance.fuel_assembly_type.model.name
    enrichment=instance.fuel_assembly_type.assembly_enrichment
    
    if instance.burnable_poison_assembly:
        str_num=str(instance.burnable_poison_assembly.rod_positions.count())
    else:
        str_num='00'
        
    tmp=str(int(enrichment*1000))+str_num
    
    return "{}/pre_robin_files/{}/{}/{}/{}".format(plant_name,file_type,assembly_name,tmp,filename)


FILE_TYPE_CHOICES=(
                    ('BASE_FUEL','BASE_FUEL'),
                    ('BP_OUT','BP_OUT'),
                    ('BR','BR'),
    )

 
# base model to contain the basic information
class BaseModel(models.Model):
    time_inserted = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    remark = models.TextField(blank=True)
    user=models.ForeignKey(User,blank=True,null=True)
    class Meta:
        abstract=True

media_root=settings.MEDIA_ROOT
#concrete model in DATABASE

    
class PreRobinModel(BaseModel):
    
    DEP_STRATEGY_CHOICES=(
                          ('LLR','LLR'),
                          ('PPC','PPC'),
                          ('LR','LR'),
                          ('PC','PC'),
    )
    POLAR_TYPE_CHOICES=(
                        ('LCMD','LCMD'),
                        ('TYPL','TYPL'),
                        ('DeCT','DeCT'),
    )
    LEAKAGE_PATH_CHOICES=(
                          (0,0),
                          (1,1),
                          (2,2),
    )
    LEAKAGE_METHOD_CHOICES=(
                            ('B1','B1'),
                            ('P1','P1'),
    )
    CONDENSATION_PATH_CHOICES=(
                               (0,0),
                               (1,1),
                               (2,2),
    )
    NUM_GROUP_2D_CHIOCES=(
                          (2,2),
                          (3,3),
                          (4,4),
                          (8,8),
                          (18,18),
                          (25,25),
                          (33,33),
    )
   
   
    
    model_name=models.CharField(max_length=32)
    

   
    #depletion state
    system_pressure=models.DecimalField(max_digits=7,decimal_places=5,default=15.51,validators=[MinValueValidator(0)],help_text='MPa')
    dep_strategy=models.CharField(max_length=3,choices=DEP_STRATEGY_CHOICES,default='LLR',blank=True,null=True)
  
    
    #accuracy_control
    track_density=models.DecimalField(max_digits=5,decimal_places=5,default=0.03,validators=[MinValueValidator(0)],help_text='cm')
    polar_type=models.CharField(max_length=4,choices=POLAR_TYPE_CHOICES,default='LCMD')
    polar_azimuth=models.CommaSeparatedIntegerField(max_length=50,default='4,16')
    iter_inner=models.PositiveSmallIntegerField(default=3)
    iter_outer=models.PositiveSmallIntegerField(default=100)
    eps_keff=models.DecimalField(max_digits=5,decimal_places=5,validators=[MinValueValidator(0)],default=1e-5)
    eps_flux=models.DecimalField(max_digits=5,decimal_places=5,validators=[MinValueValidator(0)],default=1e-4)
    #fundamental_mode
    leakage_corrector_path=models.PositiveSmallIntegerField(choices=LEAKAGE_PATH_CHOICES,default=2)
    leakage_corrector_method=models.CharField(max_length=2,choices=LEAKAGE_METHOD_CHOICES,default='B1')
    buckling_or_keff=models.DecimalField(max_digits=10,decimal_places=5,default=1)
    #energy_condensation
    condensation_path=models.PositiveSmallIntegerField(choices=CONDENSATION_PATH_CHOICES,default=1)
    num_group_2D=models.PositiveSmallIntegerField(choices=NUM_GROUP_2D_CHIOCES,default=25)
    #edit_control
    num_group_edit=models.PositiveSmallIntegerField(choices=NUM_GROUP_2D_CHIOCES,default=2)
    micro_xs_output=models.BooleanField(default=False)
    class Meta:
        db_table='pre_robin_model'
    
    def __str__(self):
        return self.model_name
      

class PreRobinInput(BaseModel):
    NUM_FUEL_CHOICES=(
                 (1,1),
                 (2,2),
                 (3,3),
    )
    NUM_EDIT_NODE_CHOICES=(
                        (16,16),
                        (4,4),
    )
    
    segment_identity=models.CharField(max_length=32)
    plant=models.ForeignKey('tragopan.Plant')
    file_type=models.CharField(max_length=9,choices=FILE_TYPE_CHOICES)
    use_pre_segment=models.ForeignKey('self',blank=True,null=True)
    pre_robin_model=models.ForeignKey(PreRobinModel,default=1)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    grid=models.ForeignKey('tragopan.Grid',blank=True,null=True)
    
    #depletion computation
    power_density=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='w/g',blank=True,null=True)
    assembly_maxium_burnup=models.DecimalField(max_digits=7,decimal_places=5,validators=[MinValueValidator(0),MaxValueValidator(100)],help_text='GWd/tU',blank=True,null=True)
    boron_density=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='ppm',blank=True,null=True)
    moderator_temperature=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='K',blank=True,null=True)
    fuel_temperature=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='K',blank=True,null=True)
    
    #reflector model computation
    core_baffle=models.ForeignKey('tragopan.CoreBaffle',blank=True,null=True)
    num_fuel_assembly=models.PositiveSmallIntegerField(choices=NUM_FUEL_CHOICES,blank=True,null=True)
    num_edit_node=models.PositiveSmallIntegerField(default=16,choices=NUM_EDIT_NODE_CHOICES,blank=True,null=True)
    #branch computation
    branch_composition=models.ManyToManyField('PreRobinBranch',related_name='branches')
    #prerobin file
    pre_robin_file=models.FileField(upload_to=get_pre_robin_upload_path,blank=True,null=True)
   
    class Meta:
        db_table='pre_robin_input'
    
    def __str__(self):
        return self.segment_identity
        

class PreRobinBranch(models.Model):
    identity=models.CharField(max_length=32)
    #the default burnup point for BOR TMO TFU CRD
    #boron density branch
    max_boron_density=models.PositiveSmallIntegerField(help_text='ppm',blank=True,null=True)
    min_boron_density=models.PositiveSmallIntegerField(default=0,help_text='ppm',blank=True,null=True)
    boron_density_interval=models.PositiveSmallIntegerField(help_text='ppm',default=200,blank=True,null=True)
    #fuel temperature branch
    max_fuel_temperature=models.PositiveSmallIntegerField(help_text='K',blank=True,null=True)
    min_fuel_temperature=models.PositiveSmallIntegerField(help_text='K',blank=True,null=True)
    fuel_temperature_interval=models.PositiveSmallIntegerField(help_text='K',default=50,blank=True,null=True)
    #moderator temperature branch
    max_moderator_temperature=models.PositiveSmallIntegerField(help_text='K',blank=True,null=True)
    min_moderator_temperature=models.PositiveSmallIntegerField(help_text='K',blank=True,null=True)
    moderator_temperature_interval=models.PositiveSmallIntegerField(help_text='K',default=4,blank=True,null=True)
    #control rod assembly branch(the even integer of default burnup) 
    control_rod_assembly=models.ForeignKey('tragopan.ControlRodAssembly',blank=True,null=True)
    #shutdown cooling branch(the even integer of default burnup) 
    shutdown_cooling_days=models.PositiveSmallIntegerField(blank=True,null=True,help_text='day')
    #xenon branch(the even integer of default burnup) 
    xenon=models.BooleanField(default=False,verbose_name='set xenon density to 0?',)
    class Meta:
        db_table='pre_robin_branch'
        verbose_name_plural='branches'
        
    def __str__(self):
        return self.identity

  
class Ibis(BaseModel):
    plant=models.ForeignKey('tragopan.Plant')
    ibis_name=models.CharField(max_length=32)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    reactor_model=models.ForeignKey('tragopan.ReactorModel')
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    active_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',default=365.80000)
    ibis_path=models.FilePathField(path=media_root,match=".*\.TAB$",recursive=True,blank=True,null=True,max_length=200)
    
    
    
    
    class Meta:
        db_table='ibis'
        order_with_respect_to='reactor_model'
        verbose_name_plural='Ibis'
        
    #validating objects(clean_fields->clean->validate_unique)
    def clean(self):
        ibis_name=self.ibis_name
        ibis_path=self.ibis_path
        units=self.plant.units.all()
        reactor_model=self.reactor_model
        reactor_model_lst=[unit.reactor_model for unit in units]
        if reactor_model not in reactor_model_lst:
            raise ValidationError({'plant':_('plant and reactor model are not compatible'), 
                                 'reactor_model':_('plant and reactor model are not compatible'),                          
            })
            
        if os.path.basename(ibis_path).split(sep='.',maxsplit=1)[0] !=ibis_name:
            raise ValidationError({'ibis_name':_('your ibis name should be the pathname stripped .TAB'),               
            })
                
        
    def get_non_bpa_basefuel(self):
        basefuels=self.base_fuels.all()

        for basefuel in basefuels:
            if not basefuel.if_insert_burnable_fuel():
                return basefuel
            
    def get_bpa_basefuel(self):
        bpa=self.burnable_poison_assembly
        if bpa:
            basefuel=self.base_fuels.get()
            return basefuel
        return None
        
    def __str__(self):
        return '{} {}'.format(self.plant,self.ibis_name)
    

class RobinFile(BaseModel):
   
    plant=models.ForeignKey('tragopan.Plant')
    file_type=models.CharField(max_length=9,choices=FILE_TYPE_CHOICES)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    input_file=models.FileField(upload_to=get_robin_upload_path)
    out1_file=models.FileField(upload_to=get_robin_upload_path)
    log_file=models.FileField(upload_to=get_robin_upload_path)
    
    class Meta:
        db_table='robin_file'
        order_with_respect_to='fuel_assembly_type'
        
        
    def __str__(self):
        return '{}'.format(self.fuel_assembly_type)


def fuel_identity_default():
    last_fuel_identity=BaseFuel.objects.filter(offset=False).last().fuel_identity
    str_num=last_fuel_identity[1:]
    try:
        num=int(str_num)+1
        return 'B'+str(num)
    except:
        return None
        
    

class BaseFuel(BaseModel):
    plant=models.ForeignKey('tragopan.Plant')
    fuel_identity=models.CharField(max_length=32,unique=True,default=fuel_identity_default)
    quadrant_one=models.ForeignKey('self',blank=True,null=True,related_name='one')
    quadrant_two=models.ForeignKey('self',blank=True,null=True,related_name='two')
    quadrant_three=models.ForeignKey('self',blank=True,null=True,related_name='three')
    quadrant_four=models.ForeignKey('self',blank=True,null=True,related_name='four')
    base_bottom=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',default=0)
    axial_composition=models.ManyToManyField(Ibis,through='BaseFuelComposition',related_name='base_fuels')
    offset=models.BooleanField(default=False)
    
    def if_insert_burnable_fuel(self):
        composition=self.composition.count()
        result=True if composition>1 else False
        return result
    
    class Meta:
        db_table='base_fuel'
        
        
        
    def __str__(self):
        return '{}'.format(self.fuel_identity)
    
class BaseFuelComposition(models.Model):
    base_fuel=models.ForeignKey(BaseFuel,related_name='composition')
    ibis=models.ForeignKey(Ibis,related_name='base_fuel_compositions')
    height=models.DecimalField(max_digits=10,decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',)
    class Meta:
        db_table='base_fuel_composition'
        
        
        
    def __str__(self):
        return '{}'.format(self.base_fuel)
    




class EgretInputXML(models.Model):
    unit=models.ForeignKey('tragopan.UnitParameter')
    base_component_path=models.FilePathField(path=media_root,match=".*base_component\.xml$",recursive=True,blank=True,null=True,max_length=200)
    base_core_path=models.FilePathField(path=media_root,match=".*base_core\.xml$",recursive=True,blank=True,null=True,max_length=200)
    loading_pattern_path=models.FilePathField(path=media_root,match=".*loading_pattern\.xml$",recursive=True,blank=True,null=True,max_length=200)
   
    
    class Meta:
        db_table='egret_input_xml'
        
    def generate_loading_pattern_doc(self,max_cycle=1):
        loading_pattern_path=self.loading_pattern_path
        dom=minidom.parse(loading_pattern_path)
        loading_pattern_node=dom.documentElement
        fuel_nodes=loading_pattern_node.getElementsByTagName('fuel')
        for fuel_node in fuel_nodes:
            cycle_num=int(fuel_node.getAttribute('cycle'))
            if cycle_num>max_cycle:
                loading_pattern_node.removeChild(fuel_node)
        
        doc = minidom.Document()
        doc.appendChild(loading_pattern_node)
        return doc
        
            
        
    def __str__(self):
        return '{}'.format(self.unit)

def get_egret_upload_path(instance,filename):
    username=instance.user.get_username()
    cycle=instance.get_cycle()
    unit=cycle.unit
    plant=unit.plant
    plant_name=plant.abbrEN
    name=os.path.basename(filename)
    task_name=instance.task_name
    return 'egret_task/{}/{}/unit{}/cycle{}/{}/{}'.format(username,plant_name,unit.unit, cycle.cycle,task_name,name) 



VISIBILITY_CHOICES=(
                         (1,'private'),
                         (2,'share to group'),
                         (3,'share to all'),
    )

       
class EgretTask(BaseModel):
    TASK_STATUS_CHOICES=(
                         (0,'waiting'),
                         (1,'calculating'),
                         (2,'suspended'),
                         (3,'stopped'),
                         (4,'finished'),
    )
    
    task_name=models.CharField(max_length=32)
    task_type=models.CharField(max_length=32)
    loading_pattern=models.ForeignKey('MultipleLoadingPattern',)
    result_path=models.FilePathField(path=media_root,match=".*\.xml$",recursive=True,blank=True,null=True,max_length=200)
    egret_input_file=models.FileField(upload_to=get_egret_upload_path,blank=True,null=True)
    task_status=models.PositiveSmallIntegerField(choices=TASK_STATUS_CHOICES,default=0)
    pre_egret_task=models.ForeignKey('self',related_name='post_egret_tasks',blank=True,null=True)
    visibility=models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES,default=2)
    authorized=models.BooleanField(default=False)
    start_time=models.DateTimeField(blank=True,null=True)
    end_time=models.DateTimeField(blank=True,null=True)
    calculation_identity=models.CharField(max_length=128,blank=True)
    
    class Meta:
        db_table='egret_task'
        
        
    #validating objects(clean_fields->clean->validate_unique)
    def clean(self):
        loading_pattern=self.loading_pattern
        pre_egret_task=self.pre_egret_task
        if pre_egret_task:
            pre_loading_pattern=pre_egret_task.loading_pattern
            if loading_pattern.get_pre_loading_pattern()!=pre_loading_pattern:
                raise ValidationError({'loading_pattern':_('loading_pattern and pre_egret_task are not compatible'),
                                       'pre_egret_task':_('loading_pattern and pre_egret_task are not compatible'),                
                })
    
    def get_cycle(self):
        cycle=self.loading_pattern.cycle
        return cycle
    get_cycle.short_description='cycle'
     
    def get_cwd(self):
        abs_file_path=self.egret_input_file.path
        dir_path=os.path.dirname(abs_file_path)
        return dir_path
        
    def get_lp_res_filename(self):
        cycle=self.get_cycle()
        unit=cycle.unit
        plant=unit.plant
        filename="{}_U{}.{}".format(plant.abbrEN,unit.unit,str(cycle.cycle).zfill(3))   
        return filename
    
    def get_follow_task_chain(self):
        cur_task=self.pre_egret_task
        follow_task_chain=[]
        while cur_task:
            follow_task_chain.insert(0, cur_task)
            cur_task=cur_task.pre_egret_task  
             
        return follow_task_chain
    
    def get_input_filename(self):
        cycle=self.get_cycle()
        unit=cycle.unit
        return 'U{}C{}.xml'.format(cycle.cycle,unit.unit)
    
    @property
    def time_cost(self):
        start_time=self.start_time
        end_time=self.end_time
        if start_time and end_time:
            time_cost=self.end_time-start_time
        else:
            time_cost=None
        return time_cost
    
    def __str__(self):
    
        return '{} {}'.format(self.user,self.task_name)

def get_custom_loading_pattern(instance,filename): 
    username=instance.user.get_username()
    name=instance.name
    cycle=instance.cycle
    unit=cycle.unit
    plant=unit.plant
    return 'multiple_loading_pattern/{}/{}/unit{}/cycle{}/{}'.format(username,plant.abbrEN,unit.unit, cycle.cycle,name+'.xml')
    
class MultipleLoadingPattern(BaseModel):
    name=models.CharField(max_length=32)
    pre_loading_pattern=models.ForeignKey('self',related_name='post_loading_patterns',blank=True,null=True)
    cycle=models.ForeignKey('tragopan.Cycle')
    xml_file=models.FileField(upload_to=get_custom_loading_pattern)
    from_database=models.BooleanField(default=False)
    authorized=models.BooleanField(default=False)
    visibility=models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES,default=3)
    class Meta:
        db_table='multiple_loading_pattern'
        unique_together=('user','name')
        
    def write_to_database(self):
        xml_file=self.xml_file
        cycle=self.cycle
        unit=cycle.unit
        reactor_model=unit.reactor_model
        reactor_positions=reactor_model.positions.all()
        f=xml_file.path
       
        dom=minidom.parse(f)
        #handle fuel     
        fuel_node=dom.getElementsByTagName('fuel')[0]
        position_nodes=fuel_node.getElementsByTagName('position')
        
        for position_node in position_nodes:
            
            row=position_node.getAttribute('row')
            column=position_node.getAttribute('column')
            reactor_position=reactor_positions.get(row=int(row),column=int(column))
            fuel_assembl_node=position_node.getElementsByTagName('fuel_assembly')[0]
        
            
            
            pk=fuel_assembl_node.getAttribute('id')
            #check if fresh
            if pk:
                fuel_assembly=FuelAssemblyRepository.objects.get(pk=pk)
                
            else: 
                type_pk=fuel_assembl_node.childNodes.item(0).data  
                fuel_assembly_type=FuelAssemblyType.objects.get(pk=type_pk)
                fuel_assembly=FuelAssemblyRepository.objects.create(type=fuel_assembly_type,unit=unit)
                
            falp=FuelAssemblyLoadingPattern.objects.create(reactor_position=reactor_position,fuel_assembly=fuel_assembly,cycle=cycle)
            print(falp)
        
        
        
    def generate_fuel_node(self):
        xml_file=self.xml_file
        cycle=self.cycle
        f=xml_file.path
       
        dom=minidom.parse(f)
        #handle bpa
        bpa_nodes=dom.getElementsByTagName('bpa')
        bpa_dic={}
        if bpa_nodes:
            bpa_node=bpa_nodes[0]
            bpa_position_nodes=bpa_node.childNodes
            for bpa_position in bpa_position_nodes:
                bpa_row=bpa_position.getAttribute('row')
                bpa_column=bpa_position.getAttribute('column')
                bpa=bpa_position.getElementsByTagName('burnable_poison_assembly')[0]
                bpa_id=bpa.getAttribute('id')
                bpa=BurnablePoisonAssembly.objects.get(pk=bpa_id)
                bpa_dic[(bpa_row,bpa_column)]=bpa
        
        #handle fuel     
        fuel_node=dom.getElementsByTagName('fuel')[0]
        position_nodes=fuel_node.getElementsByTagName('position')
        fuel_lst=[]
        #num_lst=[]
        pre_fuel_lst=[]
        for position_node in position_nodes:
            
            row=position_node.getAttribute('row')
            column=position_node.getAttribute('column')
            #num_lst.append(100*row+column)
            fuel_assembl_node=position_node.getElementsByTagName('fuel_assembly')[0]
            previous_node=position_node.getElementsByTagName('previous')
            
            type_pk=fuel_assembl_node.childNodes.item(0).data
           
            fuel_assembly_type=FuelAssemblyType.objects.get(pk=type_pk)
            
            
            
            #fresh
            if not previous_node:
                #get bpa if exist
                try:
                    burnable_poison_assembly=bpa_dic[(row,column)]
                    ibis=Ibis.objects.get(plant=cycle.unit.plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=burnable_poison_assembly)
                    bpa_basefuel=ibis.get_bpa_basefuel() 
                    fuel_lst.append(bpa_basefuel.fuel_identity)
                except:
                    ibis=Ibis.objects.get(plant=cycle.unit.plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=None)
                    non_bpa_basefuel=ibis.get_non_bpa_basefuel() 
                    fuel_lst.append(non_bpa_basefuel.fuel_identity)
                
            else:
                previous_row=previous_node[0].getAttribute('row')
                previous_column=previous_node[0].getAttribute('column')
                previous_cycle=int(previous_node[0].childNodes.item(0).data)
                position='{}{}'.format(previous_row.zfill(2), previous_column.zfill(2))
                fuel_lst.append(position)
                
                if previous_cycle!=cycle.cycle-1:
                    pre_fuel_lst.append([row,column,previous_cycle])
                    
     
        #zipped_lst=list(zip(num_lst,fuel_lst))  
        #zipped_lst.sort() 
        #fuel_lst_sorted=[item[1] for item in zipped_lst] 

        
        doc = minidom.Document()
        fuel_xml=doc.createElement('fuel')
        fuel_xml.setAttribute('cycle', str(cycle.cycle))
        map_xml=doc.createElement('map')
        fuel_xml.appendChild(map_xml)
        map_xml.appendChild(doc.createTextNode(' '.join(fuel_lst)))
        
        for item in pre_fuel_lst:
            cycle_xml=doc.createElement('cycle')
            fuel_xml.appendChild(cycle_xml)
            cycle_xml.setAttribute('col', str(item[0]))
            cycle_xml.setAttribute('row', str(item[1]))
            cycle_xml.appendChild(doc.createTextNode(str(item[2])))
        
        return fuel_xml
     
     
    def get_pre_loading_pattern(self):
        if self.pre_loading_pattern:
            pre_loading_pattern=self.pre_loading_pattern
        else:
            cycle=self.cycle
            pre_cycle=cycle.get_pre_cycle()
            if pre_cycle:
                pre_loading_pattern=MultipleLoadingPattern.objects.get(from_database=True,cycle=pre_cycle)
            else:
                pre_loading_pattern=None
        
        return pre_loading_pattern
    
                   
            
    
    def loading_pattern_chain(self):
        lst=[self,]
        pre_loading_pattern=self.get_pre_loading_pattern()
        while pre_loading_pattern:
            lst.insert(0, pre_loading_pattern)
         
            pre_loading_pattern=pre_loading_pattern.get_pre_loading_pattern()
        
          
        return lst
    
    def get_dividing_point(self):
        chain=self.loading_pattern_chain()
        chain.reverse()
        for item in chain:
            if item.from_database:
                return item
        
    
    def get_custom_fuel_nodes(self):
        fuel_node_lst=[]
        chain=self.loading_pattern_chain()
        chain.reverse()
        for item in chain:
            if not item.from_database:
                fuel_node=item.generate_fuel_node()
                fuel_node_lst.insert(0, fuel_node)
                
        return fuel_node_lst
            
        
    def __str__(self):
        return self.name
        
    
     
