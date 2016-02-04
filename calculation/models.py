from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from tragopan.models import FuelAssemblyType, BurnablePoisonAssembly,FuelAssemblyRepository, FuelAssemblyLoadingPattern,MaterialTransection,UnitParameter,PRE_ROBIN_PATH
from django.conf import settings
import os
from xml.dom import minidom 
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import shutil
from celery import signature
from datetime import datetime
from decimal import Decimal
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
media_url=settings.MEDIA_URL
#concrete model in DATABASE

    
class PreRobinModel(models.Model):
    
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
    default=models.BooleanField(default=False,help_text="set it as default",)
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
        
    def generate_accuracy_control_xml(self):
        doc=minidom.Document()
        accuracy_control_xml=doc.createElement('accuracy_control')
        
        track_density_xml=doc.createElement('track_density')
        track_density_xml.appendChild(doc.createTextNode(str(self.track_density)))
        accuracy_control_xml.appendChild(track_density_xml)
        
        polar_type_xml=doc.createElement('polar_type')
        polar_type_xml.appendChild(doc.createTextNode(str(self.polar_type)))
        accuracy_control_xml.appendChild(polar_type_xml)
        
        polar_azimuth_xml=doc.createElement('polar_azimuth')
        polar_azimuth_xml.appendChild(doc.createTextNode(str(self.polar_azimuth)))
        accuracy_control_xml.appendChild(polar_azimuth_xml)
        
        track_density_xml=doc.createElement('track_density')
        track_density_xml.appendChild(doc.createTextNode(str(self.track_density)))
        accuracy_control_xml.appendChild(track_density_xml)
        
        iter_inner_xml=doc.createElement('iter_inner')
        iter_inner_xml.appendChild(doc.createTextNode(str(self.iter_inner)))
        accuracy_control_xml.appendChild(iter_inner_xml)
        
        iter_outer_xml=doc.createElement('iter_outer')
        iter_outer_xml.appendChild(doc.createTextNode(str(self.iter_outer)))
        accuracy_control_xml.appendChild(iter_outer_xml)
        
        eps_keff_xml=doc.createElement('eps_keff')
        eps_keff_xml.appendChild(doc.createTextNode(str(self.eps_keff)))
        accuracy_control_xml.appendChild(eps_keff_xml)
        
        eps_flux_xml=doc.createElement('eps_flux')
        eps_flux_xml.appendChild(doc.createTextNode(str(self.eps_flux)))
        accuracy_control_xml.appendChild(eps_flux_xml)
        
        return accuracy_control_xml
        
    def generate_fundamental_mode_xml(self):
        doc=minidom.Document()
        fundamental_mode_xml=doc.createElement('fundamental_mode')
        
        leakage_corrector_path_xml=doc.createElement('leakage_corrector_path')
        leakage_corrector_path_xml.appendChild(doc.createTextNode(str(self.leakage_corrector_path)))
        fundamental_mode_xml.appendChild(leakage_corrector_path_xml)
        
        leakage_corrector_method_xml=doc.createElement('leakage_corrector_method')
        leakage_corrector_method_xml.appendChild(doc.createTextNode(str(self.leakage_corrector_method)))
        fundamental_mode_xml.appendChild(leakage_corrector_method_xml)
        
        buckling_or_keff_xml=doc.createElement('buckling_or_keff')
        buckling_or_keff_xml.appendChild(doc.createTextNode(str(self.buckling_or_keff)))
        fundamental_mode_xml.appendChild(buckling_or_keff_xml)
        
        return fundamental_mode_xml
    
    def generate_energy_condensation_xml(self):
        doc=minidom.Document()
        energy_condensation_xml=doc.createElement('energy_condensation')
        
        condensation_path_xml=doc.createElement('condensation_path')
        condensation_path_xml.appendChild(doc.createTextNode(str(self.condensation_path)))
        energy_condensation_xml.appendChild(condensation_path_xml)
        
        num_group_2D_xml=doc.createElement('num_group_2D')
        num_group_2D_xml.appendChild(doc.createTextNode(str(self.num_group_2D)))
        energy_condensation_xml.appendChild(num_group_2D_xml)
        
        return energy_condensation_xml
    
    def generate_edit_control_xml(self):
        doc=minidom.Document()
        edit_control_xml=doc.createElement('edit_control')
        
        num_group_edit_xml=doc.createElement('num_group_edit')
        num_group_edit_xml.appendChild(doc.createTextNode(str(self.num_group_edit)))
        edit_control_xml.appendChild(num_group_edit_xml)
        
        micro_xs_output_xml=doc.createElement('micro_xs_output')
        micro_xs_output_xml.appendChild(doc.createTextNode(str(self.num_group_2D)))
        edit_control_xml.appendChild(micro_xs_output_xml)
        
        return edit_control_xml
        
    def __str__(self):
        return self.model_name
      
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
    
    return "pre_robin_task/{}/{}/{}/{}/{}".format(plant_name,file_type,assembly_name,tmp,filename)

class PreRobinBranch(models.Model):
    unit=models.ForeignKey(UnitParameter,related_name='branches')
    default=models.BooleanField(default=False,help_text="set it as default",)
    max_burnup_point=models.DecimalField(max_digits=7,decimal_places=4,validators=[MinValueValidator(0)],default=60,help_text='GWd/tU')
    #reactor_model=models.ForeignKey(ReactorModel,related_name='branches')
    #identity=models.CharField(max_length=32)
    #the default burnup point for BOR TMO TFU CRD
    #boron density branch
    max_boron_density=models.PositiveSmallIntegerField(default=2000,help_text='ppm')
    min_boron_density=models.PositiveSmallIntegerField(default=0,help_text='ppm')
    boron_density_interval=models.PositiveSmallIntegerField(help_text='ppm',default=200)
    #fuel temperature branch
    max_fuel_temperature=models.PositiveSmallIntegerField(help_text='K',default=1253)
    min_fuel_temperature=models.PositiveSmallIntegerField(help_text='K',default=553)
    fuel_temperature_interval=models.PositiveSmallIntegerField(help_text='K',default=50,)
    #moderator temperature branch
    max_moderator_temperature=models.PositiveSmallIntegerField(help_text='K',default=615)
    min_moderator_temperature=models.PositiveSmallIntegerField(help_text='K',default=561)
    moderator_temperature_interval=models.PositiveSmallIntegerField(help_text='K',default=4)
    #control rod assembly branch(the even integer of default burnup) 
    #control_rod_assembly=models.ForeignKey('tragopan.ControlRodAssembly',blank=True,null=True)
    #shutdown cooling branch(the even integer of default burnup) 
    shutdown_cooling_days=models.PositiveSmallIntegerField(default=3000,help_text='day')
    #xenon branch(the even integer of default burnup) 
    xenon=models.BooleanField(default=False,verbose_name='set xenon density to 0?',)
    class Meta:
        db_table='pre_robin_branch'
        verbose_name_plural='branches'
        
       
    def generate_value_str(self,option):
        '''1->BOR
           2->TFU
           3->TMO
        '''
        unit=self.unit
        if option==1:
            base=unit.boron_density
            min_val=self.min_boron_density
            max_val=self.max_boron_density
            interval=self.boron_density_interval
        elif option==2:
            base=unit.fuel_temperature
            min_val=self.min_fuel_temperature
            max_val=self.max_fuel_temperature
            interval=self.fuel_temperature_interval
        elif option==3:
            base=unit.moderator_temperature
            min_val=self.min_moderator_temperature
            max_val=self.max_moderator_temperature
            interval=self.moderator_temperature_interval
           
            
        lst=list(range(min_val,max_val,interval))
        if base in lst:
            lst.remove(base)
        if max_val not in lst:
            lst.append(max_val)
        lst_str=','.join([str(i) for i in lst])
        return lst_str
        
        
    def generate_branch_xml(self,option):
        '''1->BOR
           2->TFU
           3->TMO
           4->TMO_BOR
        '''
        doc=minidom.Document()
        if option==1:
            ID='BRCH_BOR'
            name='BOR'
            value_str=self.generate_value_str(option=1)
        elif option==2:
            ID='BRCH_TFU'
            name='TFU'
            value_str=self.generate_value_str(option=2)
        elif option==3:
            ID='BRCH_TMO'
            name='TMO'
            value_str=self.generate_value_str(option=3)
            
        branch_xml=doc.createElement('base_branch')
    
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        branch_xml.appendChild(ID_xml)
    
        name_xml=doc.createElement(name)
        name_xml.appendChild(doc.createTextNode(value_str))
        branch_xml.appendChild(name_xml)
        
        return branch_xml
    
    def generate_TMO_BOR_xml(self):
        doc=minidom.Document()
        branch_xml=doc.createElement('base_branch')
        ID='BRCH_TMO_BOR'
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        branch_xml.appendChild(ID_xml)
        
        name1='TMO'
        lst_str1=self.generate_value_str(option=3)
        name1_xml=doc.createElement(name1)
        name1_xml.appendChild(doc.createTextNode(lst_str1))
        
        name2='BOR'
        lst_str2=self.generate_value_str(option=1)
        name2_xml=doc.createElement(name2)
        name2_xml.appendChild(doc.createTextNode(lst_str2))
        
        branch_xml.appendChild(name1_xml)
        branch_xml.appendChild(name2_xml)
        
        return branch_xml
        
    
    def generate_his_branch_xml(self,option):
        '''1->HCB
           2->HTF
           3->HTM
        '''
        doc=minidom.Document()
        unit=self.unit
        if option==1:
            base=unit.boron_density
            ID='HCB'
            name='BOR'
        elif option==2:
            base=unit.fuel_temperature
            ID='HTF'
            name='TFU'
        elif option==3:
            base=unit.moderator_temperature
            ID='HTM'
            name='TMO'
        branch_xml=doc.createElement('base_branch')
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        branch_xml.appendChild(ID_xml)
        
        name_xml=doc.createElement(name)
        name_xml.appendChild(doc.createTextNode(str(base)))
        branch_xml.appendChild(name_xml)  
        
        return branch_xml
    
    def generate_databank_xml(self):
        doc=minidom.Document()
        
        databank_xml=doc.createElement('branch_calc_databank')
        BOR_branch_xml=self.generate_branch_xml(option=1)
        TFU_branch_xml=self.generate_branch_xml(option=2)
        TMO_branch_xml=self.generate_branch_xml(option=3)
        
        HCB_branch_xml=self.generate_his_branch_xml(option=1)
        HTF_branch_xml=self.generate_his_branch_xml(option=2)
        HTM_branch_xml=self.generate_his_branch_xml(option=3)
        
        TMO_BOR_xml=self.generate_TMO_BOR_xml()
        
        databank_xml.appendChild(BOR_branch_xml)
        databank_xml.appendChild(TFU_branch_xml)
        databank_xml.appendChild(TMO_branch_xml)
        databank_xml.appendChild(HCB_branch_xml)
        databank_xml.appendChild(HTF_branch_xml)
        databank_xml.appendChild(HTM_branch_xml)
        databank_xml.appendChild(TMO_BOR_xml)
        
        #control rod cluster
        cra_types=self.unit.reactor_model.cra_types.all()
        for crat in cra_types:
            crat_branch_xml=crat.generate_base_branch_xml()
            BOR=self.generate_value_str(option=1)
            BOR_xml=doc.createElement('BOR')
            BOR_xml.appendChild(doc.createTextNode(BOR))
            crat_branch_xml.appendChild(BOR_xml)
            databank_xml.appendChild(crat_branch_xml)
        
        doc.appendChild(databank_xml)
        
    def __str__(self):
        return str(self.unit)
    
    
class PreRobinInput(BaseModel): 
    unit=models.ForeignKey(UnitParameter)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')  
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    task=models.ManyToManyField('PreRobinTask',through='AssemblyLamination')
    class Meta:
        db_table='pre_robin_input'
        
    @property
    def rela_file_path(self):
        fat_str=str(self.fuel_assembly_type.pk).zfill(3)
        bpa_pk=self.burnable_poison_assembly.pk
        if bpa_pk:
            bpa_str=str(bpa_pk).zfill(3)
        else:
            bpa_str="000"
        return fat_str+bpa_str
        
        
    @property
    def abs_file_path(self):
        unit=self.unit
        plant=unit.plant
        return os.path.join(PRE_ROBIN_PATH,plant.abbrEN,'unit'+str(unit.unit),self.fuel_assembly_type.assembly_name,self.rela_file_path)    
    
    def create_file_path(self):
        abs_file_path=self.abs_file_path
        if not os.path.exists(abs_file_path):
            os.makedirs(abs_file_path)
     
        return abs_file_path
    
    @property    
    def symmetry(self):
        if not self.fuel_assembly_type.symmetry:
            return False
        elif self.burnable_poison_assembly and (not self.burnable_poison_assembly.symmetry):
            return False
        else:
            return True
        
    @property
    def side_pin_num(self):
        return self.fuel_assembly_type.side_pin_num
                
    def get_height_lst(self,fuel=False):
        fuel_assembly_type=self.fuel_assembly_type
        fuel_height_lst=fuel_assembly_type.get_height_lst(fuel=fuel)
        if fuel:
            return fuel_height_lst
        burnable_poison_assembly=self.burnable_poison_assembly
        if burnable_poison_assembly:
            bp_height_lst=burnable_poison_assembly.height_lst
            height_set=set(fuel_height_lst)|set(bp_height_lst)
            height_lst=sorted(list(height_set))
        else:
            height_lst=fuel_height_lst
        
        return height_lst
    @property
    def total_height_lst(self):
        fuel_height_lst=self.get_height_lst(fuel=True)
        pin_height_lst=self.get_height_lst(fuel=False)
        height_set=set(fuel_height_lst)|set(pin_height_lst)
        height_lst=sorted(list(height_set))
        return height_lst
    def generate_transection(self,height,fuel=False):
        if self.symmetry:
            fuel_assembly_type=self.fuel_assembly_type
            fuel_transection=fuel_assembly_type.generate_transection(height,fuel=fuel)
            if fuel:
                return fuel_transection
            transection=fuel_transection
            #bpa transection
            burnable_poison_assembly=self.burnable_poison_assembly
            if burnable_poison_assembly:
                bp_transection=burnable_poison_assembly.generate_transection(height)
                transection.update(bp_transection)
                
            return transection
    
    def auto_generate_transection(self,fuel=False):
        height_lst=self.get_height_lst(fuel=fuel)
        auto_transection={}
        for height in height_lst:
            transection=self.generate_transection(height,fuel=fuel)
            auto_transection[height]=transection
        return auto_transection
    
        
    def get_lst(self,height,fuel=False):
        transection=self.generate_transection(height,fuel=fuel)
        side_num=self.side_pin_num
        half=int(side_num/2)+1
        lst=[]
        for row in range(half,side_num+1):
            for col in range(half,row+1):
                pos=(row,col)
                if pos in transection:
                    lst.append(transection[pos])
                    
                else:
                    lst.append(0)
                    
        return  lst                              
    
    def generate_pin_map_xml(self,height):
        transection=self.generate_transection(height,fuel=False)
        doc=minidom.Document()
        side_num=self.side_pin_num
        half=int(side_num/2)+1
        positions=self.fuel_assembly_type.model.positions.all()
        #pin map
        pin_map='\n'
        for row in range(half,side_num+1):
            row_lst=[]
            for col in range(half,row+1):
                #pin=positions.get(row=row,column=col)
                pos=(row,col)
                if pos in transection:
                    transection_pk=transection[pos]
                    pin_str=MaterialTransection.objects.get(pk=transection_pk).pin_id
                else:
                    pin=positions.get(row=row,column=col)
                    if pin.type=='guide':
                        pin_str='GT'
                    elif pin.type=='instrument': 
                        pin_str='IT'  
                        
                row_lst.append(pin_str)
            pin_map +=('  '.join(row_lst)+'\n')   
        pin_map_xml=doc.createElement('pin_map')
        pin_map_xml.appendChild(doc.createTextNode(pin_map))
        
        return pin_map_xml
    
    def generate_fuel_map_xml(self,height):
        return self.fuel_assembly_type.generate_fuel_map_xml(height)
    
    def get_guide_tube_xml(self):
        return self.fuel_assembly_type.model.guide_tube.generate_base_pin_xml()
    
    def get_instrument_tube_xml(self):
        return self.fuel_assembly_type.model.instrument_tube.generate_base_pin_xml()
    
    def get_base_bin(self):
        transection_dic=self.auto_generate_transection(fuel=False)
        base_bin_set=set()
        for height, transection in transection_dic.items():
            for pos,pk in transection.items():
                base_bin_set.add(pk)
                  
        return base_bin_set
    def generate_pin_databank_xml(self):
        guide_tube_xml=self.get_guide_tube_xml()
        instrument_tube_xml=self.get_instrument_tube_xml()
        
        doc=minidom.Document()
        pin_databank_xml=doc.createElement('pin_databank')
        pin_databank_xml.appendChild(guide_tube_xml)
        pin_databank_xml.appendChild(instrument_tube_xml)
        
        #fuel pin xml
        material_transections=self.get_base_bin()
        for pk in material_transections:
            mt=MaterialTransection.objects.get(pk=pk)
            base_pin_xml=mt.generate_base_pin_xml()
            pin_databank_xml.appendChild(base_pin_xml)
            
        dir_path=self.create_file_path()
        file_path=os.path.join(dir_path,'pin_databank.xml')
        f=open(file_path,'w')
        pin_databank_xml.writexml(f, '  ','  ', '\n')
        f.close()
        
    def create_depletion_state(self):
        unit=self.unit
        lst=unit.depletion_state_lst
        obj,created=DepletionState.objects.get_or_create(system_pressure=lst[0],fuel_temperature=lst[1],moderator_temperature=lst[2],boron_density=lst[3],power_density=lst[4])
        return obj
    @property
    def default_branch(self):
        unit=self.unit
        return unit.branches.get(default=True)
    @property
    def default_model(self):
        return PreRobinModel.objects.get(default=True)
    
    def create_task(self):
        fuel_assembly_type=self.fuel_assembly_type
        plant=self.unit.plant
        total_height_lst=self.total_height_lst
        branch=self.default_branch
        model=self.default_model
        depletion_state=self.create_depletion_state()
        for height in total_height_lst:
            fuel_lst=[str(item) for item in self.get_lst(height, fuel=True)]
            pin_lst=[str(item) for item in self.get_lst(height, fuel=False)]
            fuel_map=",".join(fuel_lst)
            pin_map=",".join(pin_lst)
            obj,created=PreRobinTask.objects.get_or_create(plant=plant,fuel_assembly_type=fuel_assembly_type,pin_map=pin_map,fuel_map=fuel_map,branch=branch,pre_robin_model=model,depletion_state=depletion_state)
            AssemblyLamination.objects.create(pre_robon_input=self,height=height,pre_robin_task=obj)
            
    def __str__(self):
        return "{} {} {}".format(self.unit,self.fuel_assembly_type,self.burnable_poison_assembly)
    

class AssemblyLamination(models.Model):
    pre_robon_input=models.ForeignKey(PreRobinInput)
    height =models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    pre_robin_task=models.ForeignKey('PreRobinTask')
    
    class Meta:
        db_table="assembly_lamination"
        
    def __str__(self):
        return "{} {} {}".format(self.pre_robon_input, self.height,self.pre_robin_task)

class DepletionState(models.Model):
    DEP_STRATEGY_CHOICES=(
                          ('LLR','LLR'),
                          ('PPC','PPC'),
                          ('LR','LR'),
                          ('PC','PC'),
    )
    BURNUP_UNIT_CHOICES=(
                         ('GWd/tU','GWd/tU'),
                         ('DGWd/tU','DGWd/tU'),
                         ('day','day'),
                         ('Dday','Dday'),
    )
    
    #depletion state
    system_pressure=models.DecimalField(max_digits=7,decimal_places=5,default=15.51,validators=[MinValueValidator(0)],help_text='MPa')
    burnup_point=models.DecimalField(max_digits=7,decimal_places=4,validators=[MinValueValidator(0)],default=60,help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100')
    burnup_unit=models.CharField(max_length=7,default='GWd/tU',choices=BURNUP_UNIT_CHOICES)
    fuel_temperature=models.PositiveSmallIntegerField(help_text='K',)
    moderator_temperature=models.PositiveSmallIntegerField(help_text='K',)
    boron_density=models.PositiveSmallIntegerField(help_text='ppm')
    dep_strategy=models.CharField(max_length=3,choices=DEP_STRATEGY_CHOICES,default='LLR')
    power_density=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:w/g')
    
    class Meta:
        db_table="depletion_state"
        
    
    def generate_depletion_state_xml(self):
        doc=minidom.Document()
        depletion_state_xml=doc.createElement('depletion_state')
        
        system_pressure_xml=doc.createElement('system_pressure')
        system_pressure_xml.appendChild(doc.createTextNode(str(self.system_pressure)))
        
        burnup_point_xml=doc.createElement('burnup_point')
        burnup_point_xml.appendChild(doc.createTextNode(str(-self.burnup_point)))
        
        burnup_unit_xml=doc.createElement('burnup_unit')
        burnup_unit_xml.appendChild(doc.createTextNode(self.burnup_unit))
        
        dep_strategy_xml=doc.createElement('dep_strategy')
        dep_strategy_xml.appendChild(doc.createTextNode(self.dep_strategy))
        
        power_density_xml=doc.createElement('power_density')
        power_density_xml.appendChild(doc.createTextNode(str(self.power_density)))
        
        BOR_xml=doc.createElement('BOR')
        BOR_xml.appendChild(doc.createTextNode(str(self.boron_density)))
        
        TMO_xml=doc.createElement('TMO')
        TMO_xml.appendChild(doc.createTextNode(str(self.moderator_temperature)))
        
        TFU_xml=doc.createElement('TFU')
        TFU_xml.appendChild(doc.createTextNode(str(self.fuel_temperature)))
        
        depletion_state_xml.appendChild(system_pressure_xml)
        depletion_state_xml.appendChild(burnup_point_xml)
        depletion_state_xml.appendChild(burnup_unit_xml)
        depletion_state_xml.appendChild(dep_strategy_xml)
        depletion_state_xml.appendChild(power_density_xml)
        depletion_state_xml.appendChild(BOR_xml)
        depletion_state_xml.appendChild(TMO_xml)
        depletion_state_xml.appendChild(TFU_xml)
        
        return depletion_state_xml
    def __str__(self):
        return "{} {}".format(self.pk,self.system_pressure)
    
class PreRobinTask(BaseModel):
    plant=models.ForeignKey('tragopan.Plant')
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    pin_map=models.CommaSeparatedIntegerField(max_length=256)
    fuel_map=models.CommaSeparatedIntegerField(max_length=256)
    branch=models.ForeignKey(PreRobinBranch)
    depletion_state=models.ForeignKey(DepletionState)
    pre_robin_model=models.ForeignKey(PreRobinModel)
    
    class Meta:
        db_table='pre_robin_task'
        
    @property
    def segment_ID(self):
        fuel_assembly_type=self.fuel_assembly_type
        return fuel_assembly_type.assembly_name+'_'+self.rela_file_path
        
    @property    
    def rela_file_path(self):
        return str(self.pk).zfill(5)
    
    @property
    def abs_file_path(self):
        plant=self.plant
        fuel_assembly_type=self.fuel_assembly_type
        return os.path.join(PRE_ROBIN_PATH,plant.abbrEN,'task',fuel_assembly_type.assembly_name,str(fuel_assembly_type.assembly_enrichment),self.rela_file_path) 
    
    def create_file_path(self):
        abs_file_path=self.abs_file_path
        if not os.path.exists(abs_file_path):
            os.makedirs(abs_file_path)
        return abs_file_path
    
    def get_lst(self,fuel=False):
        if fuel:
            rod_map=self.fuel_map
        else:
            rod_map=self.pin_map
            
        lst=rod_map.split(sep=',')
        
        return lst
    
    def generate_depletion_state_xml(self):
        return self.depletion_state.generate_depletion_state_xml()
    
    def generate_fuel_map_xml(self):
        fuel_lst=self.get_lst(fuel=True)
        fuel_map='\n'
        num=len(fuel_lst)
        i=0
        row=1
        while i<num:
            row_lst=fuel_lst[i:i+row]
            i +=row
            row +=1
            fuel_map +=('  '.join(row_lst)+'\n')
        doc=minidom.Document()
        fuel_map_xml=doc.createElement('fuel_map')
        fuel_map_xml.appendChild(doc.createTextNode(fuel_map))
        return fuel_map_xml
    
    def generate_pin_map_xml(self):
        pin_lst=self.get_lst(fuel=False)
        doc=minidom.Document()
        side_num=self.fuel_assembly_type.side_pin_num
        half=int(side_num/2)+1
        positions=self.fuel_assembly_type.model.positions.all()
        #pin map
        pin_map='\n'
        num=len(pin_lst)
        i=0
        row=1
        while i<num:
            row_lst=[]
            line_lst=pin_lst[i:i+row]
            #handle one row
            for j in range(len(line_lst)):
                real_col=half+j
                real_row=half+row-1
                pk=int(line_lst[j])
                #GT or IT
                if pk==0:
                    pin=positions.get(row=real_row,column=real_col)
                    if pin.type=='guide':
                        pin_str='GT'
                    elif pin.type=='instrument': 
                        pin_str='IT' 
                else:
                    pin_str=MaterialTransection.objects.get(pk=pk).pin_id
                
                row_lst.append(pin_str)
            
            pin_map +=('  '.join(row_lst)+'\n') 
            i +=row
            row +=1       
              
        pin_map_xml=doc.createElement('pin_map')
        pin_map_xml.appendChild(doc.createTextNode(pin_map))
        return pin_map_xml
        
        
    def generate_assembly_model_xml(self):
        assembly_model_xml=self.fuel_assembly_type.model.generate_assembly_model_xml()
        fuel_map_xml=self.generate_fuel_map_xml()
        pin_map_xml=self.generate_pin_map_xml()
        
        assembly_model_xml.appendChild(fuel_map_xml)
        assembly_model_xml.appendChild(pin_map_xml)
        return assembly_model_xml
    
    def generate_calculation_segment_xml(self):
        assembly_model_xml=self.generate_assembly_model_xml()
        depletion_state_xml=self.generate_depletion_state_xml()
        
        doc=minidom.Document()
        calculation_segment_xml=doc.createElement('calculation_segment')
        segment_ID_xml=doc.createElement('segment_ID')
        segment_ID_xml.appendChild(doc.createTextNode(self.segment_ID))
        
        #prerobin default
        pre_robin_model=self.pre_robin_model
        accuracy_control_xml=pre_robin_model.generate_accuracy_control_xml()
        fundamental_mode_xml=pre_robin_model.generate_fundamental_mode_xml()
        energy_condensation_xml=pre_robin_model.generate_energy_condensation_xml()
        edit_control_xml=pre_robin_model.generate_edit_control_xml()
        
        calculation_segment_xml.appendChild(segment_ID_xml)
        calculation_segment_xml.appendChild(assembly_model_xml)
        calculation_segment_xml.appendChild(depletion_state_xml)
        
        calculation_segment_xml.appendChild(accuracy_control_xml)
        calculation_segment_xml.appendChild(fundamental_mode_xml)
        calculation_segment_xml.appendChild(energy_condensation_xml)
        calculation_segment_xml.appendChild(edit_control_xml)
        return calculation_segment_xml
    def __str__(self):
        return "{} {}".format(self.fuel_assembly_type,self.pin_map)

  
class Ibis(BaseModel):
    plant=models.ForeignKey('tragopan.Plant')
    ibis_name=models.CharField(max_length=32)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    reactor_model=models.ForeignKey('tragopan.ReactorModel')
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    active_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',default=365.80000)
    #ibis_path=models.FilePathField(path=media_root,match=".*\.TAB$",recursive=True,blank=True,null=True,max_length=200)

    class Meta:
        db_table='ibis'
        order_with_respect_to='reactor_model'
        verbose_name_plural='Ibis'
        
    #validating objects(clean_fields->clean->validate_unique)
    def clean(self):
        units=self.plant.units.all()
        reactor_model=self.reactor_model
        reactor_model_lst=[unit.reactor_model for unit in units]
        if reactor_model not in reactor_model_lst:
            raise ValidationError({'plant':_('plant and reactor model are not compatible'), 
                                 'reactor_model':_('plant and reactor model are not compatible'),                          
            })
    
    @property
    def ibis_path(self):
        ibis_dir=self.plant.ibis_dir
        name=self.ibis_name+'.TAB'
        ibis_path=os.path.join(ibis_dir,name)
        if os.path.isfile(ibis_path):
            return ibis_path
        
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
        composition_set=self.composition_set
        
        return True if composition_set[1] else False
    
    @property
    def composition_set(self):
        fuel_assembly_set=set()
        bpa_set=set()
        for item in self.axial_composition.all():
            fuel_assembly=item.fuel_assembly_type
            bpa=item.burnable_poison_assembly 
            if fuel_assembly:
                fuel_assembly_set.add(fuel_assembly)
            if bpa:
                bpa_set.add(bpa)  
            
        return (fuel_assembly_set,bpa_set)
    
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
    




def get_egret_upload_path(instance,filename):
    username=instance.user.get_username()
    cycle=instance.cycle
    unit=cycle.unit
    plant=unit.plant
    plant_name=plant.abbrEN
    recalculation_depth=instance.recalculation_depth
    name="upload_{}.xml".format(str(recalculation_depth).zfill(6))
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
                         (5,'cancled'),
                         (6,'errored'),
    )
    TASK_TYPE_CHOICES=(
                       ('FOLLOW','follow'),
                       ('SEQUENCE', 'auto sequence'),
    )
    
    task_name=models.CharField(max_length=32)
    task_type=models.CharField(max_length=32,choices=TASK_TYPE_CHOICES)
    loading_pattern=models.ForeignKey('MultipleLoadingPattern',blank=True,null=True)
    egret_input_file=models.FileField(upload_to=get_egret_upload_path,blank=True,null=True)
    task_status=models.PositiveSmallIntegerField(choices=TASK_STATUS_CHOICES,default=0)
    pre_egret_task=models.ForeignKey('self',related_name='post_egret_tasks',blank=True,null=True)
    visibility=models.PositiveSmallIntegerField(choices=VISIBILITY_CHOICES,default=2)
    authorized=models.BooleanField(default=False)
    start_time=models.DateTimeField(blank=True,null=True)
    end_time=models.DateTimeField(blank=True,null=True)
    calculation_identity=models.CharField(max_length=128,blank=True)
    recalculation_depth=models.PositiveSmallIntegerField(default=1)
    locked=models.BooleanField(default=False)
    class Meta:
        db_table='egret_task'
        #unique_together = ("user", "task_name")
        
    def if_recalculated(self):
        if self.recalculation_depth>1:
            return True
        else:
            return False
    if_recalculated.boolean=True 
    if_recalculated.short_description="whether recalculated:True/False"   
    #validating objects(clean_fields->clean->validate_unique)
    def clean(self):
        loading_pattern=self.get_loading_pattern()
        pre_egret_task=self.pre_egret_task
        if pre_egret_task:
            pre_loading_pattern=pre_egret_task.loading_pattern
            #locked=pre_egret_task.locked
            
            #if locked:
            #    raise ValidationError({
            #                           'pre_egret_task':_('your pre egret task is locked, please wait a moment'),                
            #    })
            
            if self.task_type=='FOLLOW':
                if loading_pattern.get_pre_loading_pattern()!=pre_loading_pattern:
                    raise ValidationError({'loading_pattern':_('loading_pattern and pre_egret_task are not compatible'),
                                           'pre_egret_task':_('loading_pattern and pre_egret_task are not compatible'),                
                    })
                    
            #assure pre egret task is finished     
            if pre_egret_task.task_status!=4:
                raise ValidationError({
                                       'pre_egret_task':_('pre_egret_task must be finished'),                
                })
                
        else:
            cycle_num=self.get_loading_pattern().cycle.cycle
            if cycle_num!=1:
                raise ValidationError({
                                       'pre_egret_task':_('you need to provide a previous egret task'),                
                })
                
        #check if the task_name repeated
        #if EgretTask.objects.filter(task_name=self.task_name,user=self.user,loading_pattern=self.get_loading_pattern()):
        #raise ValidationError({
        #                           'task_name':_('the taskname already exists with respect to user and loading_pattern'),                
        #        })
            
        #check sequence task type
        if self.task_type=='SEQUENCE':
            if self.loading_pattern:
                raise ValidationError({
                                       'loading_pattern':_('you donnot need to provide a loading pattern when processing sequence task'),                
                })
                
            
    def get_loading_pattern(self):
        if self.task_type=='FOLLOW':
            return self.loading_pattern
        elif self.task_type=='SEQUENCE':
            return self.pre_egret_task.loading_pattern 
              
    @property
    def cycle(self):
        cycle=self.get_loading_pattern().cycle
        return cycle
    
    @property
    def unit(self):
        return self.cycle.unit
    
    @property
    def plant(self):
        return self.unit.plant
     
    def get_cwd(self):
        abs_file_path=self.egret_input_file.path
        dir_path=os.path.dirname(abs_file_path)
        return dir_path
    
    @property
    def result_file(self):
        cwd=self.get_cwd()
        workspace_dir=os.path.join(cwd,'.workspace')
        abs_path=os.path.join(workspace_dir,self.get_lp_res_filename()+'.xml')
        rel_path=os.path.relpath(abs_path,media_root)
        return os.path.join(media_url,rel_path)
        
    
        
    def get_lp_res_filename(self):
        
        cycle=self.cycle
        unit=self.unit
        plant=self.plant
        filename="{}_U{}.{}".format(plant.abbrEN,unit.unit,str(cycle.cycle).zfill(3))   
        return filename
    
    def mv_case_res_file(self):
        if self.task_type=='FOLLOW':
            '''move the .LP .RES in workspace to the upper directory'''
            name=self.get_lp_res_filename()
            cwd=self.get_cwd()
            
            
            #if this is not the first calculation,you should rename the .CASE and .RES files that already exist
            if self.recalculation_depth>1:
                #depth=str(self.recalculation_depth-1).zfill(6)
                #rename the previous .CASE and .RES files
                #os.rename(os.path.join(cwd,name+'.CASE'),os.path.join(cwd,name+'.CASE.'+depth+'.old'))
                #os.rename(os.path.join(cwd,name+'.RES'),os.path.join(cwd,name+'.RES.'+depth+'.old'))
                if os.path.isfile(os.path.join(cwd,name+'.CASE')): 
                    os.remove(os.path.join(cwd,name+'.CASE')) 
                if os.path.isfile(os.path.join(cwd,name+'.RES')):    
                    os.remove(os.path.join(cwd,name+'.RES')) 
                             
            #move sub directory to current directory
            sub_cwd=os.path.join(cwd,'.workspace')
            CASE_path=os.path.join(sub_cwd,name+'.CASE')
            RES_path=os.path.join(sub_cwd,name+'.RES')
            shutil.move(CASE_path,cwd)
            shutil.move(RES_path,cwd)
            
            
        
    
    def cp_lp_res_file(self):
        follow_task_chain=self.get_follow_task_chain()
        for follow_task in follow_task_chain:
            cwd=follow_task.get_cwd()
            lp_res_filename=follow_task.get_lp_res_filename()
            lp_file=os.path.join(cwd,lp_res_filename+'.LP')
            res_file=os.path.join(cwd,lp_res_filename+'.RES')
            os.link(lp_file,lp_res_filename+'.LP' )
            os.link(res_file,lp_res_filename+'.RES')
            if self.task_type =='SEQUENCE':
                case_file=os.path.join(cwd,lp_res_filename+'.CASE')
                os.link(case_file,lp_res_filename+'.CASE')
    
    def get_follow_task_chain(self):
        cur_task=self.pre_egret_task
        follow_task_chain=[]
        while cur_task:
            follow_task_chain.insert(0, cur_task)
            cur_task=cur_task.pre_egret_task  
             
        return follow_task_chain
    
    def get_input_filename(self):
        cycle=self.cycle
        unit=cycle.unit
        if self.task_type=='FOLLOW':
            recalculation_depth=self.recalculation_depth
            return 'U{}C{}_{}.xml'.format(unit.unit,cycle.cycle,str(recalculation_depth).zfill(6))
        elif self.task_type=='SEQUENCE':
            return 'U{}C{}_sequence.xml'.format(unit.unit,cycle.cycle)
    
    def start_calculation(self,countdown):
        cwd=self.get_cwd()
        user=self.user.username
        input_filename=self.get_input_filename()
        start_time=datetime.now()
        self.start_time=start_time
        if countdown!=0:
            self.task_status=0
        self.save() 
        s=signature('calculation.tasks.egret_calculation_task', args=(cwd,input_filename,user,self.pk), countdown=countdown)
        s.freeze()
        self.calculation_identity=s.id
        self.save()
        s.delay()
        
    
    @property
    def time_cost(self):
        start_time=self.start_time
        end_time=self.end_time
        if start_time and end_time:
            time_cost=self.end_time-start_time
        else:
            time_cost=None
        return time_cost
    
    #@property
    #def egret_input_xml(self):
    #    loading_pattern=self.get_loading_pattern()
    #    unit=loading_pattern.cycle.unit
    #    egret_input_xml=EgretInputXML.objects.get(unit=unit)
    #    return egret_input_xml
        
    
    def generate_runegret_xml(self,restart=0,export=1):
        #loading_pattern=self.get_loading_pattern()
        cycle=self.cycle
        cycle_num=cycle.cycle
        unit=cycle.unit
        unit_num=unit.unit
        plant=unit.plant
        plant_name=plant.abbrEN
        core_id="{}_U{}".format(plant_name,unit_num)
        
        ibis_dir=plant.ibis_dir
        
        #egret_input_xml=self.egret_input_xml
        doc=minidom.Document()
        run_egret_xml=doc.createElement('run_egret')
        doc.appendChild(run_egret_xml)
        run_egret_xml.setAttribute('core_id', core_id)
        run_egret_xml.setAttribute('cycle',str(cycle_num))
        #xml path
        base_core_path=unit.base_core_path
        base_component_path=unit.base_component_path
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
        if self.task_type=='FOLLOW':
            cycle_depl_xml=doc.createElement('cycle_depl')
            cycle_depl_xml.setAttribute('restart', str(restart))
            cycle_depl_file=os.path.basename(self.egret_input_file.name)
            cycle_depl_xml.appendChild(doc.createTextNode(cycle_depl_file))
            run_egret_xml.appendChild(cycle_depl_xml)
            
        elif self.task_type=='SEQUENCE':
            cycle_sequ_xml=doc.createElement('cycle_sequ')
            cycle_sequ_file=os.path.basename(self.egret_input_file.name)
            cycle_sequ_xml.appendChild(doc.createTextNode(cycle_sequ_file))
            run_egret_xml.appendChild(cycle_sequ_xml)
            
            
        
        #export_case
        export_case_xml=doc.createElement('export_case')
        export_case_xml.appendChild(doc.createTextNode(str(export)))
        run_egret_xml.appendChild(export_case_xml)
        
        #ibis directory
        ibis_path_xml=doc.createElement('ibis_dir')
        ibis_path_xml.appendChild(doc.createTextNode(ibis_dir))
        run_egret_xml.appendChild(ibis_path_xml)
        input_filename=self.get_input_filename()
        run_egret_file=open(input_filename,'w')
        doc.writexml(run_egret_file,indent='  ',addindent='  ', newl='\n',)
        run_egret_file.close()
    
    def generate_loading_pattern_xml(self):
        unit=self.unit
        #egret_input_xml=self.egret_input_xml
        loading_pattern=self.get_loading_pattern()
        #from database loading pattern xml
        dividing_point=loading_pattern.get_dividing_point()     
        custom_fuel_nodes=loading_pattern.get_custom_fuel_nodes()
        loading_pattern_doc=unit.generate_loading_pattern_doc(max_cycle=dividing_point.cycle.cycle)
        loading_pattern_node=loading_pattern_doc.documentElement
       
        for custom_fuel_node in custom_fuel_nodes:
            loading_pattern_node.appendChild(custom_fuel_node)
        #custom loading pattern xml
        loading_pattern_file=open('loading_pattern.xml','w')
        loading_pattern_doc.writexml(loading_pattern_file,indent='  ',addindent='  ', newl='\n',)
        loading_pattern_file.close()
        
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
                    print(pre_fuel_lst)
     
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
            cycle_xml.setAttribute('col', str(item[1]))
            cycle_xml.setAttribute('row', str(item[0]))
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
        
    
     
