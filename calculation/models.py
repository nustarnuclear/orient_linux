from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from tragopan.models import FuelAssemblyType, BurnablePoisonAssembly,FuelAssemblyRepository, FuelAssemblyLoadingPattern,MaterialTransection,UnitParameter,PRE_ROBIN_PATH,BasicMaterial,Material,ReactorModel
from django.conf import settings
import os,signal
from xml.dom import minidom 
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import shutil,re
from celery import signature
from datetime import datetime
from subprocess import Popen
from django.core.files import File
import time
from decimal import Decimal
import socket
from orient.celery import app
# Create your models here.
TASK_STATUS_CHOICES=(
                         (0,'waiting'),
                         (1,'calculating'),
                         (2,'suspended'),
                         (3,'stopped'),
                         (4,'finished'),
                         (5,'canceled'),
                         (6,'error'),
    )

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    return s.getsockname()[0]


def get_symmetry(fuel_assembly_type,burnable_poison_assembly=None):
    fuel_symmetry=fuel_assembly_type.symmetry
    bpa_symmetry=burnable_poison_assembly.symmetry if burnable_poison_assembly else True
    return fuel_symmetry and bpa_symmetry
    
def parse_xml_to_lst(src,dest):
    f=open(src)
    line_lst=f.readlines()
    f.close()
    title=re.compile('<\?.*\?>')
    start=re.compile('<.*>')
    end=re.compile('</.*>')
    total=re.compile('<.*>.*</.*>',re.DOTALL)
    result_lst=[]
    for i in range(len(line_lst)):
        line=line_lst[i]
        
        #this is a tile 
        if title.search(line):
            continue
        #this is a end element
        end_element=end.search(line)  
        if end_element:
            matched=end_element.group(0)
            if re.search(matched.replace('/',''), result_lst[-1]):
                result_lst[-1] +=line
            else:
                result_lst.append(line)
                
            continue    
        #this is a start element
        if start.search(line):
            result_lst.append(line)
            continue
        #this is a context    
        else:
            result_lst[-1] +=line
            
    index=0
    for i in range(len(result_lst)):
        line=result_lst[i]
        split_lst=re.split('[<>]', line)
        if total.search(line):
            assert(len(split_lst)==5)
            #add "" when contains /
            if split_lst[2].find("/")>=0:
                result_lst[i]='  '*index+split_lst[1]+' = '+'"'+split_lst[2]+'"'+'\n'
            else:
                result_lst[i]='  '*index+split_lst[1]+' = '+split_lst[2]+'\n'
        else:
            if split_lst[1].startswith('/'):
                index -=1
                result_lst[i]='  '*index+split_lst[1]+'\n'
            else:
                result_lst[i]='  '*index+split_lst[1]+':'+'\n'
                index +=1
    

    filename=os.path.basename(src)  
    new_filename=filename.replace('.xml','.txt') 
    new_path=os.path.join(dest,new_filename)         
    sfile=open(new_path,'w')
    sfile.writelines(result_lst)
    sfile.close()
    return new_path

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

class Server(models.Model):
#     STATUS_CHOICES=(("A","available"),
#                     ("B","busy"),
#     )
    name=models.CharField(max_length=32,unique=True)
    IP=models.GenericIPAddressField(unique=True)
    #status=models.CharField(max_length=1,default="A",choices=STATUS_CHOICES)
    queue=models.CharField(max_length=32,unique=True)
    class Meta:
        db_table="server"
        ordering=['IP']
    @property
    def available(self):
        pre_robin_tasks=self.pre_robin_tasks.all()
        for task in pre_robin_tasks:
            if not task.robin_finished:
                return False
        
        return True
   
    @classmethod
    def first(cls):
        available_servers=cls.objects.exclude(name="Controller")
        if available_servers.exists():
            return available_servers.first()
        else:
            return cls.objects.first()
        
    def next(self):
        next_servers=Server.objects.exclude(name="Controller").filter(IP__gt=self.IP)
        if next_servers.exists():
            return next_servers.first()
        else:
            return Server.first()
        
    def __str__(self):
        return "{} {}".format(self.name, self.IP)
    

    
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
        micro_xs_output_xml.appendChild(doc.createTextNode(str(self.micro_xs_output)))
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
    #unit=models.ForeignKey(UnitParameter,related_name='branches')
    #default=models.BooleanField(default=False,help_text="set it as default",)
    reactor_model=models.OneToOneField(ReactorModel)
    max_burnup_point=models.DecimalField(max_digits=7,decimal_places=4,validators=[MinValueValidator(0)],default=60,help_text='GWd/tU')
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
    #shutdown cooling branch(the even integer of default burnup) 
    shutdown_cooling_days=models.PositiveSmallIntegerField(default=3000,help_text='day')
    #xenon branch(the even integer of default burnup) 
    xenon=models.BooleanField(default=False,verbose_name='set xenon density to 0?',)
    class Meta:
        db_table='pre_robin_branch'
        verbose_name_plural='branches'
        
    
#     @property
#     def rela_file_path(self):
#         pk=self.pk
#         return str(pk).zfill(3)
#         
#     @property
#     def abs_file_path(self):
#         unit=self.unit
#         plant=unit.plant
#         return os.path.join(PRE_ROBIN_PATH,plant.abbrEN,'unit'+str(unit.unit),'branch',self.rela_file_path)    
#     
#     def create_file_path(self):
#         abs_file_path=self.abs_file_path
#         if not os.path.exists(abs_file_path):
#             os.makedirs(abs_file_path)
#      
#         return abs_file_path
    
        
       
    def generate_value_str(self,option):
        '''1->BOR
           2->TFU
           3->TMO
        '''
        reactor_model=self.reactor_model
        if option==1:
            base=reactor_model.boron_density
            min_val=self.min_boron_density
            max_val=self.max_boron_density
            interval=self.boron_density_interval
        elif option==2:
            base=reactor_model.fuel_temperature
            min_val=self.min_fuel_temperature
            max_val=self.max_fuel_temperature
            interval=self.fuel_temperature_interval
        elif option==3:
            base=reactor_model.moderator_temperature
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
    
    @property
    def base_branch_ID_lst(self):
        return ['BRCH_BOR','BRCH_TFU','BRCH_TMO']
    
    
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
        
    
    def generate_his_branch_xml(self,option='HCB'):

        doc=minidom.Document()
        reactor_model=self.reactor_model
        if option=='HCB':
            base=reactor_model.boron_density
            name='BOR'
        elif option=='HTF':
            base=reactor_model.fuel_temperature
            name='TFU'
        elif option=='HTM':
            base=reactor_model.moderator_temperature
            name='TMO'
        branch_xml=doc.createElement('base_branch')
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(option))
        branch_xml.appendChild(ID_xml)
        
        name_xml=doc.createElement(name)
        name_xml.appendChild(doc.createTextNode(str(base)))
        branch_xml.appendChild(name_xml)  
        
        return branch_xml

    def get_his_lst(self,option='HCB'):
        '''
        option: HCB,HTM,HTF
        '''
        reactor_model=self.reactor_model
        if option=='HCB':
            base=reactor_model.boron_density
            HCB_lst=[0,500,1000,1500,2000]
            if base in HCB_lst:
                HCB_lst.remove(base)
            return HCB_lst

        elif option=='HTM':
            base=reactor_model.moderator_temperature
            interval=15
        elif option=='HTF':
            base=reactor_model.fuel_temperature
            interval=200
            
        return [base-2*interval,base-interval,base+interval,base+2*interval,]
    
    def generate_databank_xml(self,branch_file_path='branch_calc_databank.xml'):
        #generate a branch file in current working directory
        doc=minidom.Document()
        
        databank_xml=doc.createElement('branch_calc_databank')
        BOR_branch_xml=self.generate_branch_xml(option=1)
        TFU_branch_xml=self.generate_branch_xml(option=2)
        TMO_branch_xml=self.generate_branch_xml(option=3)
        
        HCB_branch_xml=self.generate_his_branch_xml(option='HCB')
        HTF_branch_xml=self.generate_his_branch_xml(option='HTF')
        HTM_branch_xml=self.generate_his_branch_xml(option='HTM')
        
        TMO_BOR_xml=self.generate_TMO_BOR_xml()
        
        databank_xml.appendChild(BOR_branch_xml)
        databank_xml.appendChild(TFU_branch_xml)
        databank_xml.appendChild(TMO_branch_xml)
        databank_xml.appendChild(HCB_branch_xml)
        databank_xml.appendChild(HTF_branch_xml)
        databank_xml.appendChild(HTM_branch_xml)
        databank_xml.appendChild(TMO_BOR_xml)
        
        #control rod cluster
        cra_types=self.reactor_model.cra_types.all()
        for crat in cra_types:
            crat_branch_xml_lst=crat.generate_base_branch_xml_lst()
            for crat_branch_xml in crat_branch_xml_lst:
                BOR=self.generate_value_str(option=1)
                BOR_xml=doc.createElement('BOR')
                BOR_xml.appendChild(doc.createTextNode(BOR))
                crat_branch_xml.appendChild(BOR_xml)
                databank_xml.appendChild(crat_branch_xml)
        
        doc.appendChild(databank_xml)
        
        branch_file=open(branch_file_path,'w')
        doc.writexml(branch_file,indent='  ',addindent='  ', newl='\n',)
        branch_file.close()
        return branch_file_path
        
    def __str__(self):
        return str(self.reactor_model)
    
    
class PreRobinInput(BaseModel): 
    unit=models.ForeignKey(UnitParameter)
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')  
    burnable_poison_assembly=models.ForeignKey('tragopan.BurnablePoisonAssembly',blank=True,null=True)
    task=models.ManyToManyField('PreRobinTask',through='AssemblyLamination')
    class Meta:
        db_table='pre_robin_input'
        unique_together = ("unit","fuel_assembly_type", "burnable_poison_assembly")
        
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
        return get_symmetry(self.fuel_assembly_type, self.burnable_poison_assembly)
    @property
    def basefuel_ID(self):
        return "B"+str(self.pk)  
    @property
    def active_length(self):
        return self.fuel_assembly_type.model.active_length
        
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
    
        
    def create_depletion_state(self):
        unit=self.unit
        lst=unit.depletion_state_lst
        obj,created=DepletionState.objects.get_or_create(system_pressure=lst[0],fuel_temperature=lst[1],moderator_temperature=lst[2],boron_density=lst[3],power_density=lst[4])
        return obj

    @property
    def default_model(self):
        return PreRobinModel.objects.get(default=True)
    
    def create_branch(self):
        reactor_model=self.unit.reactor_model
        obj,created=PreRobinBranch.objects.get_or_create(reactor_model=reactor_model)
        return obj
    def create_task(self):
        #
        if self.task.exists():
            return
        fuel_assembly_type=self.fuel_assembly_type
        plant=self.unit.plant
        total_height_lst=self.total_height_lst
        branch=self.create_branch()
        model=self.default_model
        depletion_state=self.create_depletion_state()
        for height in total_height_lst:
            fuel_lst=[str(item) for item in self.get_lst(height, fuel=True)]
            pin_lst=[str(item) for item in self.get_lst(height, fuel=False)]
            fuel_map=",".join(fuel_lst)
            pin_map=",".join(pin_lst)
            obj,created=PreRobinTask.objects.get_or_create(plant=plant,fuel_assembly_type=fuel_assembly_type,pin_map=pin_map,fuel_map=fuel_map,branch=branch,pre_robin_model=model,depletion_state=depletion_state,)
            AssemblyLamination.objects.create(pre_robon_input=self,height=height,pre_robin_task=obj)
            
    def generate_base_fuel_xml(self):
        doc=minidom.Document()
        base_fuel_xml=doc.createElement("base_fuel")
        active_length=self.active_length
        fuel_id=self.basefuel_ID
        offset=0
        base_bottom=0
        #set attribute
        base_fuel_xml.setAttribute("active_length", str(active_length))
        base_fuel_xml.setAttribute("fuel_id", str(fuel_id))
        base_fuel_xml.setAttribute("offset", str(offset))
        base_fuel_xml.setAttribute("base_bottom", str(base_bottom))
        
        #assembly laminations
        layers=self.layers.all()
        length_lst,segment_ID_lst=zip(*[(layer.length,layer.pre_robin_task.segment_ID) for layer in layers])
        length_lst=[str(length) for length in length_lst]
        axial_ratio_xml=doc.createElement("axial_ratio")
        axial_ratio_xml.appendChild(doc.createTextNode(" ".join(length_lst)))
        base_fuel_xml.appendChild(axial_ratio_xml)
        
        axial_color_xml=doc.createElement("axial_color")
        axial_color_xml.appendChild(doc.createTextNode(" ".join(segment_ID_lst)))
        base_fuel_xml.appendChild(axial_color_xml)
        #grid
        grid_positions=self.fuel_assembly_type.model.grid_positions.all()
        for grid_position in grid_positions:
            grid=grid_position.grid
            hight=grid_position.height
            width=grid.sleeve_height
            type_num=grid.type_num
            spacer_grid_xml=doc.createElement("spacer_grid")
            spacer_grid_xml.setAttribute("hight",str(hight))
            spacer_grid_xml.setAttribute("width",str(width))
            spacer_grid_xml.appendChild(doc.createTextNode(str(type_num)))
            base_fuel_xml.appendChild(spacer_grid_xml)
            
        #if offset add one more BX fuel
        if not self.symmetry:
            BX_fuel_id="BX"+str(self.pk)
            offset=1
            BX_base_fuel_xml=doc.createElement("base_fuel")
            
            BX_base_fuel_xml.setAttribute("fuel_id", BX_fuel_id)
            BX_base_fuel_xml.setAttribute("offset", str(offset))
            
            #get non bpa basefuel
            pre_robin_input=PreRobinInput.objects.get(unit=self.unit,fuel_assembly_type=self.fuel_assembly_type,burnable_poison_assembly=None)
            non_bpa_fuel_id=pre_robin_input.basefuel_ID
            burnable_poison_assembly=self.burnable_poison_assembly
            quadrant_symbol_lst=burnable_poison_assembly.get_quadrant_symbol()
            if quadrant_symbol_lst in [[1],[2],[3],[4]]:
                inner_part_lst=[fuel_id,non_bpa_fuel_id,non_bpa_fuel_id,non_bpa_fuel_id]
            elif quadrant_symbol_lst in [[1,2],[1,3],[3,4],[2,4]]:
                inner_part_lst=[fuel_id,fuel_id,non_bpa_fuel_id,non_bpa_fuel_id]
            elif quadrant_symbol_lst in [[1,2,3],[2,3,4],[1,2,4],[1,3,4]]:
                inner_part_lst=[fuel_id,fuel_id,fuel_id,non_bpa_fuel_id] 
            index=1    
            for inner_part in inner_part_lst:
                inner_part_xml=doc.createElement("inner_part")
                inner_part_xml.setAttribute("quadrant", str(index))
                inner_part_xml.appendChild(doc.createTextNode(inner_part))
                BX_base_fuel_xml.appendChild(inner_part_xml)
                index +=1
        else:
            BX_base_fuel_xml=None
                
        return (base_fuel_xml,BX_base_fuel_xml)
    
    @classmethod
    def generate_base_component_xml(cls,reactor_model): 
        doc=minidom.Document()
        base_component_xml=doc.createElement("base_component")
        base_component_xml.setAttribute("basecore_ID", reactor_model.name)
        pre_robin_inputs=cls.objects.filter(unit__reactor_model=reactor_model)
        
        for pre_robin_input in pre_robin_inputs:
            base_fuel_xml,BX_base_fuel_xml=pre_robin_input.generate_base_fuel_xml()
            base_component_xml.appendChild(base_fuel_xml)
            if BX_base_fuel_xml:
                base_component_xml.appendChild(BX_base_fuel_xml)
                
        cra_types=reactor_model.cra_types.all()
        for cra_type in cra_types:
            base_control_rod_xml=cra_type.generate_base_control_rod_xml()
            base_component_xml.appendChild(base_control_rod_xml)
        doc.appendChild(base_component_xml)
        filename="base_component.xml"
        f=open(filename,"w")
        doc.writexml(f, indent="  ", addindent="  ", newl="\n")
        f.close()
        return os.path.join(os.getcwd(),filename) 
    
    @classmethod
    def write_base_component_xml(cls):
        reactor_models=ReactorModel.objects.all()
        
        for reactor_model in reactor_models:
            name=reactor_model.name
            file_path=os.path.join(PRE_ROBIN_PATH,name)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            os.chdir(file_path)
            cls.generate_base_component_xml(reactor_model)
    
    def cut_already(self):
        return True  if self.layers.exists() else False 
    cut_already.boolean=True  
     
    @classmethod
    def auto_add(cls,unit):
        base_fuel_set=unit.generate_base_fuel_set()
        index=0
        for base_fuel in base_fuel_set:
            obj, created =cls.objects.get_or_create(unit=unit,fuel_assembly_type=base_fuel[0],burnable_poison_assembly=base_fuel[1])
            if created:
                index+=1
        return index
    
    @classmethod
    def generate_loading_pattern_xml(cls,unit):
        unit_num=unit.unit
        plant=unit.plant
        plant_name=plant.abbrEN
        cycles=unit.cycles.all()
        reactor_model=unit.reactor_model
        reactor_positions=reactor_model.positions.all()
        basecore_id=reactor_model.name
        core_id=plant_name+'_U%d'%unit_num
        #start xml 
        doc = minidom.Document()
        loading_pattern_xml = doc.createElement("loading_pattern")
        loading_pattern_xml.setAttribute("basecore_ID",basecore_id)
        loading_pattern_xml.setAttribute("core_id",core_id)
        doc.appendChild(loading_pattern_xml)
        
        #control rod xml
        
        for cycle in cycles:
            control_rod_assembly_loading_patterns=cycle.control_rod_assembly_loading_patterns.all()
            if control_rod_assembly_loading_patterns:
                control_rod_xml=doc.createElement("control_rod")
                control_rod_xml.setAttribute("cycle",str(cycle.cycle))
                loading_pattern_xml.appendChild(control_rod_xml)
                
                map_xml=doc.createElement("map")
                control_rod_xml.appendChild(map_xml)
                cra_position_lst=[]
                for reactor_position in reactor_positions:
                    cra_pattern=control_rod_assembly_loading_patterns.filter(reactor_position=reactor_position)
                    if cra_pattern:
                        crat=cra_pattern.get().control_rod_assembly.cluster.control_rod_assembly_type
                        cra_position_lst.append(crat.cr_id)
                    else:
                        cra_position_lst.append('0')
                        
                map_xml.appendChild(doc.createTextNode((' '.join(cra_position_lst))))
        
        #fuel xml
        for cycle in cycles: 
            fuel_lst=[]
            previous_cycle_lst=[]
            rotation_lst=[]
            for reactor_position in reactor_positions:
                    fuel_assembly_loading_pattern=cycle.fuel_assembly_loading_patterns.get(reactor_position=reactor_position)
                    #rotation
                    rotation_degree=fuel_assembly_loading_pattern.rotation_degree
                    if rotation_degree!='0':
                        rotation_lst.append([rotation_degree,reactor_position.row,reactor_position.column])
                        
                    
                    #not fresh
                    if fuel_assembly_loading_pattern.get_previous():
                        [previous_cycle,previous_position_row,previous_position_column]=fuel_assembly_loading_pattern.get_previous().split('-')
                        position='{}{}'.format(previous_position_row.zfill(2), previous_position_column.zfill(2))
                        fuel_lst.append(position)
                        #not from last cycle
                        if previous_cycle!=cycle.cycle-1:
                            previous_cycle_lst.append([previous_cycle,reactor_position.row,reactor_position.column])
                           
                    #fresh       
                    else:
                        fuel_assembly_type=fuel_assembly_loading_pattern.fuel_assembly.type
                        bpa_patterns=cycle.bpa_loading_patterns.filter(reactor_position=reactor_position)
                        bpa=bpa_patterns.get().burnable_poison_assembly.get_symmetry_bpa() if bpa_patterns.exists() else None
                        pre_robin_input=cls.objects.get(unit=unit,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=bpa)
                        base_fuel_ID=pre_robin_input.basefuel_ID
                        if bpa and (not bpa.symmetry):
                            base_fuel_ID=base_fuel_ID.replace("B","BX")
                        fuel_lst.append(base_fuel_ID)
                                 
            
            fuel_xml = doc.createElement("fuel")
            fuel_xml.setAttribute("cycle",str(cycle.cycle))
            loading_pattern_xml.appendChild(fuel_xml)
            
            fuel_map_xml=doc.createElement("map")
            fuel_xml.appendChild(fuel_map_xml)
            fuel_map_xml.appendChild(doc.createTextNode((' '.join(fuel_lst))))
            
            #handle the fuel assembly not from last cycle
            for previous_cycle_info in previous_cycle_lst:
                if int(previous_cycle_info[0])!=cycle.cycle-1:
                    
                    cycle_xml=doc.createElement("cycle")
                    cycle_xml.setAttribute('row',str(previous_cycle_info[1]))
                    cycle_xml.setAttribute('col',str(previous_cycle_info[2]))
                    cycle_xml.appendChild(doc.createTextNode(previous_cycle_info[0]))
                    fuel_xml.appendChild(cycle_xml)
                    
            
            #handle fuel assembly rotation
            for item in rotation_lst:
                rotation_xml=doc.createElement("rotation")
                rotation_xml.setAttribute('row',str(item[1]))
                rotation_xml.setAttribute('col',str(item[2]))
                rotation_xml.appendChild(doc.createTextNode(str(int(item[0])/90+1)))
                fuel_xml.appendChild(rotation_xml)
                
        filename='loading_pattern.xml'         
        f = open(filename,"w")
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        f.close()
        return os.path.join(os.getcwd(),filename) 
    
    @classmethod
    def write_loading_pattern_xml(cls):
        units=UnitParameter.objects.all()
        
        for unit in units:
            plant=unit.plant
            file_path=os.path.join(PRE_ROBIN_PATH,plant.abbrEN,'unit'+str(unit.unit))
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            os.chdir(file_path)
            cls.generate_loading_pattern_xml(unit)
        
    def __str__(self):
        return "{} {} {}".format(self.unit,self.fuel_assembly_type,self.burnable_poison_assembly)
    

class AssemblyLamination(models.Model):
    pre_robon_input=models.ForeignKey(PreRobinInput,related_name="layers")
    height =models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],verbose_name="bottom_height",help_text='unit:cm')
    pre_robin_task=models.ForeignKey('PreRobinTask')
    
    class Meta:
        db_table="assembly_lamination"
    
    @property
    def length(self):
        post_layer=self.post_layer
        height=self.height
        return (post_layer.height-height) if post_layer else (self.pre_robon_input.active_length-height)
    
    @property
    def post_layer(self):
        post_layers=AssemblyLamination.objects.filter(pre_robon_input=self.pre_robon_input).order_by("height").filter(height__gt=self.height)
        if post_layers.exists():
            return post_layers.first()
        else:
            return None
        
        
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
                         ('DGWd/tU"','DGWd/tU'),
                         ('day','day'),
                         ('Dday','Dday'),
    )
    
    #depletion state
    system_pressure=models.DecimalField(max_digits=7,decimal_places=5,default=15.51,validators=[MinValueValidator(0)],help_text='MPa')
    burnup_point=models.DecimalField(max_digits=7,decimal_places=4,validators=[MinValueValidator(0)],default=60,help_text='0.0,0.03,0.05,0.1,0.2,0.5,1,2,3,...,10,12,14,16,...,100')
    burnup_unit=models.CharField(max_length=9,default='GWd/tU',choices=BURNUP_UNIT_CHOICES)
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
    
def server_default():
    last_task=PreRobinTask.objects.last()
    if last_task:
        return last_task.server.next()
    else:
        return Server.first()
    
class PreRobinTask(BaseModel):
    plant=models.ForeignKey('tragopan.Plant')
    fuel_assembly_type=models.ForeignKey('tragopan.FuelAssemblyType')
    pin_map=models.CommaSeparatedIntegerField(max_length=256)
    fuel_map=models.CommaSeparatedIntegerField(max_length=256)
    branch=models.ForeignKey(PreRobinBranch)
    depletion_state=models.ForeignKey(DepletionState)
    pre_robin_model=models.ForeignKey(PreRobinModel)
    task_status=models.PositiveSmallIntegerField(choices=TASK_STATUS_CHOICES,default=0)
    server=models.ForeignKey(Server,related_name="pre_robin_tasks",default=server_default)
    #symmetry=models.BooleanField(default=True)
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
    
    #without fuel transection
    @property
    def material_transection_set(self):
        lst=self.get_lst(fuel=False)
        material_transection_set=set(lst)
        material_transection_set.remove('0')
        return material_transection_set
    
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
    
    @property
    def segment_file_path(self):
        abs_file_path=self.abs_file_path
        return os.path.join(abs_file_path,'calculation_segments.xml')
    
    def generate_base_segment_xml(self):
        assembly_model_xml=self.generate_assembly_model_xml()
        depletion_state_xml=self.generate_depletion_state_xml()
        
        doc=minidom.Document()
        base_segment_xml=doc.createElement('base_segment')
        segment_ID_xml=doc.createElement('segment_ID')
        segment_ID_xml.appendChild(doc.createTextNode(self.segment_ID))
        
        branch_calc_ID_xml=doc.createElement('branch_calc_ID')
        base_branch_ID_lst=self.branch.base_branch_ID_lst
        branch_calc_ID_xml.appendChild(doc.createTextNode(','.join(base_branch_ID_lst)))
        base_segment_xml.appendChild(branch_calc_ID_xml)
        #prerobin default
        pre_robin_model=self.pre_robin_model
        accuracy_control_xml=pre_robin_model.generate_accuracy_control_xml()
        fundamental_mode_xml=pre_robin_model.generate_fundamental_mode_xml()
        energy_condensation_xml=pre_robin_model.generate_energy_condensation_xml()
        edit_control_xml=pre_robin_model.generate_edit_control_xml()
        
        base_segment_xml.appendChild(segment_ID_xml)
        base_segment_xml.appendChild(assembly_model_xml)
        base_segment_xml.appendChild(depletion_state_xml)
        
        base_segment_xml.appendChild(accuracy_control_xml)
        base_segment_xml.appendChild(fundamental_mode_xml)
        base_segment_xml.appendChild(energy_condensation_xml)
        base_segment_xml.appendChild(edit_control_xml)
        
        return base_segment_xml
        
        
    def generate_his_segment_lst(self,option='HCB'):
        '''
        option:HCB,HTF,HTM
        '''
        segment_lst=[]
        his_lst=self.branch.get_his_lst(option=option)
        for item in his_lst:
            doc=minidom.Document()
            base_segment_xml=doc.createElement('base_segment')
            use_pre_segment_xml=doc.createElement('use_pre_segment')
            base_segment_ID=self.segment_ID
            use_pre_segment_xml.appendChild(doc.createTextNode(base_segment_ID))
            base_segment_xml.appendChild(use_pre_segment_xml)
            
            segment_ID=base_segment_ID+'_'+option+'_'+str(item)
            segment_ID_xml=doc.createElement('segment_ID')
            segment_ID_xml.appendChild(doc.createTextNode(segment_ID))
            base_segment_xml.appendChild(segment_ID_xml)
                
            branch_calc_ID_xml=doc.createElement('branch_calc_ID')
            branch_calc_ID_xml.appendChild(doc.createTextNode(option))  
            base_segment_xml.appendChild(branch_calc_ID_xml)  
            
            #depletion state
            depletion_state_xml=doc.createElement('depletion_state')
            if option=='HCB':
                value='BOR'
            elif option=='HTM':
                value='TMO'
            elif option=='HTF':
                value='TFU'
                
            value_xml=doc.createElement(value)
            value_xml.appendChild(doc.createTextNode(str(item)))
            depletion_state_xml.appendChild(value_xml)
            base_segment_xml.appendChild(depletion_state_xml)
            
            segment_lst.append(base_segment_xml)
        return segment_lst
    

          
    def generate_grid_segment_lst(self):
        fuel_assembly_model=self.fuel_assembly_type.model
        total_grid_type_num=fuel_assembly_model.total_grid_type_num
        segment_lst=[]
    
        for type_num in range(1,total_grid_type_num):
            grid=fuel_assembly_model.grids.filter(type_num=type_num).first()
            moderator_material_ID=grid.moderator_material_ID
            doc=minidom.Document()
            base_segment_xml=doc.createElement('base_segment')
            use_pre_segment_xml=doc.createElement('use_pre_segment')
            base_segment_ID=self.segment_ID
            use_pre_segment_xml.appendChild(doc.createTextNode(base_segment_ID))
            base_segment_xml.appendChild(use_pre_segment_xml)
            
            segment_ID=base_segment_ID+'_GRID_'+str(type_num)
         
            segment_ID_xml=doc.createElement('segment_ID')
            segment_ID_xml.appendChild(doc.createTextNode(segment_ID))
            base_segment_xml.appendChild(segment_ID_xml)  
            
            branch_calc_ID_xml=doc.createElement('branch_calc_ID')
            branch_calc_ID_xml.appendChild(doc.createTextNode(''))
            base_segment_xml.appendChild(branch_calc_ID_xml)  
            
            assembly_model_xml=doc.createElement('assembly_model')
            moderator_mat_xml=doc.createElement('moderator_mat')
            moderator_mat_xml.appendChild(doc.createTextNode(moderator_material_ID))
            assembly_model_xml.appendChild(moderator_mat_xml)
            base_segment_xml.appendChild(assembly_model_xml) 
            
            segment_lst.append(base_segment_xml)
            
        return segment_lst
    
    def generate_calculation_segments_xml(self):
        doc=minidom.Document()
        calculation_segments_xml=doc.createElement('calculation_segments')
        doc.appendChild(calculation_segments_xml)
        #base
        base_segment_xml=self.generate_base_segment_xml()
        calculation_segments_xml.appendChild(base_segment_xml)
        
        #grid
        grid_segment_lst=self.generate_grid_segment_lst()
        for grid_segment in grid_segment_lst:
            calculation_segments_xml.appendChild(grid_segment)
        
        #history
        HCB_segment_lst=self.generate_his_segment_lst(option='HCB')
        for HCB_segment in HCB_segment_lst:
            calculation_segments_xml.appendChild(HCB_segment)
            
        HTF_segment_lst=self.generate_his_segment_lst(option='HTF')
        for HTF_segment in HTF_segment_lst:
            calculation_segments_xml.appendChild(HTF_segment)
        
        HTM_segment_lst=self.generate_his_segment_lst(option='HTM')
        for HTM_segment in HTM_segment_lst:
            calculation_segments_xml.appendChild(HTM_segment)
            
            
        
        segment_file_path=self.segment_file_path
        segment_file=open(segment_file_path,'w')
        doc.writexml(segment_file,indent='  ',addindent='  ', newl='\n',)
        segment_file.close()
        
        return segment_file_path
      
    def generate_pin_databank_xml(self,pin_databank_path='pin_databank.xml'):
        fuel_assembly_type=self.fuel_assembly_type
        fuel_assembly_model=fuel_assembly_type.model
        guide_tube=self.fuel_assembly_type.model.guide_tube
        guide_tube_xml=guide_tube.generate_base_pin_xml()
        instrument_tube_xml=fuel_assembly_model.instrument_tube.generate_base_pin_xml()
        
        doc=minidom.Document()
        pin_databank_xml=doc.createElement('pin_databank')
        pin_databank_xml.appendChild(guide_tube_xml)
        pin_databank_xml.appendChild(instrument_tube_xml)
        
        #fuel pin xml
        material_transection_set=self.material_transection_set
           
        #control rod pin 
        reactor_model=self.plant.reactor_model
        control_rod_types=reactor_model.control_rod_types.all()
        for control_rod_type in control_rod_types:
            material_transection_set.update(control_rod_type.generate_material_transection_set())
        
        for pk in material_transection_set:
            mt=MaterialTransection.objects.get(pk=pk)
            base_pin_xml=mt.generate_base_pin_xml(guide_tube)
            pin_databank_xml.appendChild(base_pin_xml) 
       
        f=open(pin_databank_path,'w')
        pin_databank_xml.writexml(f, '  ','  ', '\n')
        f.close()
        return pin_databank_path
    
    @property
    def input_file_path(self):
        abs_file_path=self.create_file_path()
        input_file_path=os.path.join(abs_file_path,'input_file_info.inp')
        return input_file_path
    
    def generate_prerobin_input(self):
        abs_file_path=self.create_file_path()
        os.chdir(abs_file_path)
        input_file_path=self.input_file_path
        f=open(input_file_path,'w')
        f.write('& INPUT_FILE_INFO\n')
        
        #material_element.lib comes from table BasicMaterial 
        material_element_lib_path=BasicMaterial.material_element_lib_path
        if not os.path.exists(material_element_lib_path):
            BasicMaterial.generate_material_lib()
        f.write('    material_element_lib    = "%s"\n'%material_element_lib_path)
        
        #hydro_table is in the PRE_ROBIN_PATH
        hydro_table_path=os.path.join(PRE_ROBIN_PATH,'hydro.table')
        f.write('    hydro_table             = "%s"\n'%hydro_table_path)
        
        #material_databank comes from table Material
        material_databank_path=Material.material_databank_path
        if not os.path.exists(material_databank_path):
            Material.generate_material_databank_xml()
        #convert xml to sread format
        material_databank=parse_xml_to_lst(material_databank_path,abs_file_path) 
        f.write('    material_databank       = "%s"\n'%material_databank)
        
        #pin_databank comes from table PreRobinInput
        pin_databank_path=self.generate_pin_databank_xml()
        pin_databank=parse_xml_to_lst(pin_databank_path,abs_file_path) 
        f.write('    pin_databank            = "%s"\n'%pin_databank)
           
        #branch_calculation_info
        branch_file_path=self.branch.generate_databank_xml()
        branch_file=parse_xml_to_lst(branch_file_path,abs_file_path) 
        f.write('    branch_calculation_info = "%s"\n'%branch_file) 
         
        #calculation_segments
        segment_file_path=self.generate_calculation_segments_xml()
        segment_file=parse_xml_to_lst(segment_file_path,abs_file_path) 
        f.write('    calculation_segments    = "%s"\n'%segment_file)
        
        f.write('/\n')
        f.close()
        
    def generate_prerobin_output(self):
        abs_file_path=self.create_file_path()
        os.chdir(abs_file_path)
        input_file_path=self.input_file_path
        if not os.path.exists(input_file_path):
            self.generate_prerobin_input()
        process=Popen(['/opt/nustar/bin/myprerobin','-i',input_file_path])
        return_code=process.wait()
        return return_code
    
    def generate_robin_tasks(self,postfix=None):
        abs_file_path=self.abs_file_path
        os.chdir(abs_file_path)
        inputfile_names=self.find_inputfile_names(postfix)
        for inputfile_name in inputfile_names:
            f=open(inputfile_name)
            RobinTask.objects.create(name=inputfile_name.rstrip('.inp'),pre_robin_task=self,input_file=File(f))
            f.close()
            
    def start_prerobin(self):
        return_code=self.generate_prerobin_output()
        #base
        self.generate_robin_tasks()
        #grid
        self.generate_robin_tasks('GRID')
        #HTM
        self.generate_robin_tasks('HTM')
        #HTF
        self.generate_robin_tasks('HTF')
        #HCB
        self.generate_robin_tasks('HCB')
        if return_code!=0:
            self.task_status=6
        else:  
            self.task_status=4
        self.save()
        return return_code
        
    def start_robin(self):
        robin_tasks=self.robin_tasks.all()
        for robin_task in robin_tasks:
            #if waiting
            if robin_task.task_status==0:
                time.sleep(1)
                robin_task.start_calculation()
    
    def stop_robin(self): 
        server=self.server
        queue=server.queue+"_control"
        s=signature('calculation.tasks.stop_robin_task', args=(self.pk,))
        s.freeze()
        s.apply_async(queue=queue,task_id=str(self.pk)) 
        
            
    def find_inputfile_names(self,postfix=None):
        base_segment_ID=self.segment_ID
        abs_file_path=self.abs_file_path
        filenames=os.listdir(abs_file_path)
        inputfile_names=[]
        if postfix:
            name=base_segment_ID+'_'+postfix+'_.+\.inp'
        else:
            name=base_segment_ID+'\.inp'
            
        name_pattern=re.compile(name)
        for filename in filenames:
            if name_pattern.fullmatch(filename):
                inputfile_names.append(filename) 
        return inputfile_names
    
    def create_subdir(self):
        abs_file_path=self.abs_file_path
        sub_dir=os.path.join(abs_file_path,'IDYLL')
        
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir) 
        return sub_dir
               
    def cp_out_to_subdir(self,subdir):
        robin_tasks=self.robin_tasks.all()
        for robin_task in robin_tasks:
            cwd=robin_task.get_cwd()
            output_filename=robin_task.get_output_filename()
            shutil.copy(os.path.join(cwd,output_filename),subdir)
            
    def get_idyll_input(self):
        abs_file_path=self.abs_file_path
        segment_ID=self.segment_ID
        return os.path.join(abs_file_path,"IDYLL_"+segment_ID+".inp")
    
    def generate_ptc_wet(self):
        fuel_assembly_type=self.fuel_assembly_type
        fuel_assembly_model=fuel_assembly_type.model
        f=open("PTC_WET.INP",'w')
        f.write("N_PTC_BU\n")
        f.write("3\n")
        f.write("ptc_bu(1:N_PTC_BU)\n")
        f.write("10 80 150\n")
        f.write("ptc_deltaT(0:N_PTC_BU)\n")
        enrichment=fuel_assembly_type.assembly_enrichment
        if enrichment>=Decimal(3.1):
            f.write("292 292 260 260\n")
        else:
            f.write("292 292 292 292\n")
            
        total_grid_type_num=fuel_assembly_model.total_grid_type_num
        f.write("N_SPA\n")
        f.write("{}\n".format(total_grid_type_num))
        f.write("spa_fraction\n")
        volume_fraction_lst=[]
        for type_num in range(1,total_grid_type_num+1):
            grid=fuel_assembly_model.grids.filter(type_num=type_num).first()
            volume_fraction=grid.volume_fraction
            volume_fraction_lst.append(str(volume_fraction))
        f.write(' '.join(volume_fraction_lst)+"\n")
        
        f.write("wet_fraction\n")
        
        reactor_model=self.plant.reactor_model
        control_rod_type=reactor_model.control_rod_types.first()
        
        wet_frac=fuel_assembly_model.get_wet_frac()
        wet_frac_rodin=fuel_assembly_model.get_wet_frac_rodin(control_rod_type)
        f.write("{} {} \n".format(wet_frac, wet_frac_rodin))
        
        f.close()
        
    def start_idyll(self): 
        idyll_input=self.get_idyll_input()
        subdir=self.create_subdir()
        os.chdir(subdir)  
        #create idyll dirs
        try:
            os.mkdir("CHECK_INPUT")
            os.mkdir("CHECK_POW")
            os.mkdir("CHECK_TABLE")
            os.mkdir("TABLE_OUTPUT")
        except:
            pass
        #generate ptc_wet file
        self.generate_ptc_wet()
        #cp idyll into subdir
        shutil.copy(idyll_input,os.path.join(subdir,"IBIS.INP"))
        #cp out1 into subdir
        self.cp_out_to_subdir(subdir)
        
        process=Popen(['/opt/nustar/bin/myidyll',"IBIS.INP"])
        return_code=process.wait()
        return return_code
    
    @property    
    def robin_finished(self):
        if self.robin_tasks.exclude(task_status=4).exists():
            return False
        else:
            return True
      
 
    def __str__(self):
        #return "{} {}".format(self.pk,self.fuel_assembly_type)
        return self.segment_ID
    

def get_robintask_upload_path(instance,filename):
    name=instance.name
    pre_robin_task=instance.pre_robin_task
    plant=pre_robin_task.plant
    fuel_assembly_type=pre_robin_task.fuel_assembly_type
    model_name=fuel_assembly_type.model.name
    enrichment=fuel_assembly_type.assembly_enrichment
    return "robin_task/{}/{}/{}/{}/{}".format(plant.abbrEN,model_name,enrichment,name,filename)

class RobinTask(models.Model):
    name=models.CharField(max_length=64)
    pre_robin_task=models.ForeignKey(PreRobinTask,related_name="robin_tasks")
    input_file=models.FileField(upload_to=get_robintask_upload_path)
    task_status=models.PositiveSmallIntegerField(choices=TASK_STATUS_CHOICES,default=0)
    start_time=models.DateTimeField(blank=True,null=True)
    end_time=models.DateTimeField(blank=True,null=True)
    #pid=models.PositiveSmallIntegerField(blank=True,null=True)
    class Meta:
        db_table='robin_task'
        
    def get_cwd(self):
        abs_file_path=self.input_file.path
        dir_path=os.path.dirname(abs_file_path)
        return dir_path
    def get_input_filename(self):
        abs_file_path=self.input_file.path
        basename=os.path.basename(abs_file_path)
        return basename
    
    def get_output_filename(self):
        input_filename=self.get_input_filename()
        return input_filename.rstrip(".inp")+".out1"
    
    def get_log_filename(self):
        input_filename=self.get_input_filename()
        return input_filename.rstrip(".inp")+".log"

    def get_logfile_url(self):
        input_fileurl=self.input_file.url
        url=input_fileurl.rstrip(".inp")+".log"
        return url
    
    def get_outfile_url(self):
        input_fileurl=self.input_file.url
        url=input_fileurl.rstrip(".inp")+".out1"
        return url
    
    def start_calculation(self):
        server=self.pre_robin_task.server
        queue=server.queue
        s=signature('calculation.tasks.robin_calculation_task', args=(self.pk,))
        s.freeze()
        s.apply_async(queue=queue,task_id=str(self.pk))   
        
    def cancel_calculation(self):
        #only can cancel waiting tasks
        app.control.revoke(str(self.pk),)
        self.task_status=5
        self.save()
    
    def stop_calculation(self):
        #only can stop calculating tasks
        pid=self.pid
        os.kill(pid,signal.SIGKILL)
        while True:
            if self.task_status==4:
                self.task_status=3
                self.save()
                break
            else:
                time.sleep(1)
                self.refresh_from_db()
            
    @property
    def pid(self):
        cwd=self.get_cwd()
        os.chdir(cwd)
        f=open("myrobin.pid")
        pid= int(f.read())
        f.close()
        return pid
           
        
        
    def __str__(self):
        return self.name
    
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
        
    
     
