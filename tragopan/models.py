from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Max,Sum,Min
#token generated automatically when creating a new user
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import os
import tempfile
import math
from xml.dom import minidom
from decimal import Decimal
from django.core.files import File
from django.contrib.auth.models import User
import django.dispatch
#define some signals
del_fieldfile=django.dispatch.Signal(providing_args=["pk",])

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    else:
        token=Token.objects.get(user=instance)
        token.delete()
        Token.objects.create(user=instance)
        
def which_section(height,height_lst):
    if type(height)==Decimal:
        pass
    else:
        height=Decimal(str(height))
   
    for i in range(len(height_lst)):
        if height_lst[i]>height:
            return i
        elif height_lst[i]==height:
            return i+1
            
    return len(height_lst)

def format_line(lst,width=16):
    result_lst=[]
    for item in lst:
        blank_num=width-len(str(item))
        result_lst.append(str(item)+' '*blank_num)
    result_lst.append('\n')
    return ''.join(result_lst) 

def in_triangle(row,column,side_num):
    '''to check if this position is in the 1/8 part to be calculated
    1|2
    ---
    3|4
    the lower triangle of quadrant 4
    '''
    half=int(side_num/2)+1
    if row>=half and column>=half and column<=row:
        return True
    else:
        return False
        
def generate_quadrant_symbol(row,column,side_num):
    '''
    1|2
    ---
    3|4
    '''
    
    half=int(side_num/2)+1
    if row<=half:
        if column<=half:
            return 1
        else:
            return 2
    else:
        if column<=half:
            return 3
        else:
            return 4

def reflect_4th_quandrant(row,column,side_num):
        half=int(side_num/2)+1
        quadrant=generate_quadrant_symbol(row,column,side_num)
        if quadrant==1:
            row_4th=2*half-row
            col_4th=2*half-column
        elif quadrant==2:
            row_4th=column
            col_4th=half+half-row
            
        elif quadrant==3:
            row_4th=half+half-column
            col_4th=row
        else:
            row_4th=row
            col_4th=column
        return (row_4th,col_4th)
    
#some common constant
MEDIA_ROOT=settings.MEDIA_ROOT
PRE_ROBIN_PATH=os.path.join(MEDIA_ROOT,'pre_robin')
# base model to contain the basic information
class BaseModel(models.Model):
    time_inserted = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    remark = models.TextField(blank=True)
    class Meta:
        abstract=True

#################################################       
# Concrete models in accordance with the database
#################################################

#################################################
#basic information 
#################################################

#describe element information
class Element(BaseModel):
    atomic_number = models.PositiveSmallIntegerField(primary_key=True)
    symbol = models.CharField(max_length=8,unique=True)
    nameCH = models.CharField(max_length=8)
    nameEN = models.CharField(max_length=40)
    reference = models.CharField(max_length=80, default='IUPAC')
    
    
    
    @staticmethod
    def autocomplete_search_fields():
        return ("atomic_number__iexact", "symbol__icontains",)
    
    class Meta:
        db_table='element'
        ordering=['atomic_number']
    def __str__(self):
        return self.symbol

    


class Nuclide(BaseModel):
    element = models.ForeignKey(Element,to_field="symbol",related_name='nuclides',related_query_name='nuclide')
    atom_mass = models.DecimalField(max_digits=9,decimal_places=6,validators=[MinValueValidator(0)])
    abundance = models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    reference = models.CharField(max_length=80, default='IUPAC') 
   
    class Meta:
        
        db_table='nuclide'
        unique_together = ('element', 'atom_mass')
        ordering=['element']
            
    def __str__(self):
        return "{}{}".format(self.element, round(self.atom_mass))
    
class WimsNuclideData(BaseModel):
    NF_CHOICES=(
                (0,'无共振积分表'),
                (1,'有共振积分表的非裂变核'),
                (2,'有共振吸收共振积分表的可裂变核'),
                (3,'有共振吸收和共振裂变共振积分表的可裂变核'),
                (4,'没有共振积分表的可裂变核'),
    )
    MATERIAL_TYPE_CHOICES=(
                           ('M','慢化剂'),
                           ('FP','裂变产物'),
                           ('A','锕系核素'),
                           ('B','可燃核素'),
                           ('D','用于剂量的材料'),
                           ('S','结构材料和其他'),
                           ('B/FP','可燃核素 /裂变产物'),
    )
    element = models.ForeignKey(Element,blank=True,null=True)
    nuclide_name= models.CharField(max_length=30,) 
    id_wims=models.PositiveIntegerField(unique=True,blank=True,null=True)
    id_self_defined=models.PositiveIntegerField(unique=True,blank=True,null=True)
    amu= models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),])
    nf=models.PositiveSmallIntegerField(choices=NF_CHOICES)
    material_type= models.CharField(max_length=4,choices=MATERIAL_TYPE_CHOICES)
    descrip= models.CharField(max_length=50)
    class Meta:
        db_table='wims_nuclide_data'
        verbose_name_plural='wims nuclide data'
    @staticmethod
    def autocomplete_search_fields():
        return ("element__symbol",'id_wims','id_self_defined')
    
    @property
    def res_trig(self):
        return 0 if self.nf in (0,4) else 1

    @property
    def dep_trig(self):
        return 1 if self.material_type in ('FP','A','B','B/FP') else 0
  
    @classmethod
    def generate_nuclide_lib(cls):
        data=cls.objects.exclude(material_type='D')
        for item in data:
            id_wims=item.id_wims if item.id_wims else 0
            yield (item.id_self_defined,id_wims,item.amu,item.res_trig,item.dep_trig)  
            
    def __str__(self):
        return "{}".format(self.nuclide_name)
  
class WmisElementData(BaseModel):
    element_name=models.CharField(max_length=30,)
    composition=models.ManyToManyField(WimsNuclideData,through='WmisElementComposition')
    class Meta:
        db_table='wmis_element_data'
        verbose_name_plural='wmis element data'
    @staticmethod
    def autocomplete_search_fields():
        return ("element_name__icontains",)
    def get_nuclide_num(self):  
        return self.composition.count()
    def __str__(self):
        return self.element_name
    
class WmisElementComposition(BaseModel):
    wmis_element=models.ForeignKey(WmisElementData,related_name='nuclides')
    wmis_nuclide=models.ForeignKey(WimsNuclideData)
    weight_percent=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    
    class Meta:
        db_table='wmis_element_composition'
        
    def __str__(self):
        return '{} {}'.format(self.wmis_element, self.wmis_nuclide)
    
class BasicMaterial(BaseModel):
    TYPE_CHOICES=(
                           (1,'Compound or elementary substance'),
                           (2,'alloy'),
    )
    name=models.CharField(max_length=16,unique=True)
    type=models.PositiveSmallIntegerField(default=1,choices=TYPE_CHOICES)
    composition=models.ManyToManyField(WmisElementData,through='BasicElementComposition')
    density=models.DecimalField(max_digits=15, decimal_places=8,help_text=r'unit:g/cm3',blank=True,null=True)
    class Meta:
        db_table='basic_material'
    def get_element_num(self):
        return self.composition.count()
    def weight_percent_sum(self):
        return self.elements.all().aggregate(weight_percent_sum=Sum('weight_percent'))['weight_percent_sum']
    
    def data_integrity(self):
        result=self.weight_percent_sum()
        if result:
            if abs(result-100)>=10e-1:
                return False
        return True
    data_integrity.boolean=True
       
    def get_name(self,enrichment=None):
        if self.name=="UO2":
            return self.name+"_"+str(enrichment)
        else:
            return self.name
    #class attribute
    material_element_lib_path=os.path.join(PRE_ROBIN_PATH,'material_element.lib')
    
    @classmethod
    def generate_material_lib(cls):
        if not os.path.exists(PRE_ROBIN_PATH):
            os.makedirs(PRE_ROBIN_PATH)
        f=open(cls.material_element_lib_path,'w')
        
        #write general info
        general_descrip=['nuclides','elements','compounds','mixtures']
        f.write(format_line(general_descrip))
        
        nuclide_num=WimsNuclideData.objects.exclude(material_type='D').count()
        element_num=WmisElementData.objects.count()
        compound_num=cls.objects.filter(type=1).count()
        mixture_num=cls.objects.filter(type=2).count()
        f.write(format_line([nuclide_num,element_num,compound_num,mixture_num]))
        f.write('\n')
        #write nuclides info
        nuclide_descrip=['isotope','ID in lib','amu','res_trig','dep_trig']
        f.write(format_line(nuclide_descrip))
        for item in WimsNuclideData.generate_nuclide_lib():
            f.write(format_line(item))
        f.write('\n')    
        #write elements info
        f.write('elements:\n')
        for element in WmisElementData.objects.all():
            element_descrip=[element.element_name,element.get_nuclide_num()]
            f.write(format_line(element_descrip))
            for compo in element.nuclides.order_by('wmis_nuclide__amu'):
                nuclide_info=[' ',compo.wmis_nuclide.id_self_defined,compo.weight_percent/100] 
                f.write(format_line(nuclide_info))
        f.write('\n')        
        #write compounds info
        f.write('compounds:\n')
        for compound in cls.objects.filter(type=1):
            compound_descrip=[compound.name,compound.get_element_num(),compound.density]
            f.write(format_line(compound_descrip))
            for compo in compound.elements.all():
                element_info=[' ',compo.wims_element.element_name,compo.weight_percent/100 if compo.weight_percent else compo.element_number]
                f.write(format_line(element_info))
        f.write('\n') 
        
        #write mixture info
        f.write('mixtures:\n')
        for mixture in cls.objects.filter(type=2):
            mixture_descrip=[mixture.name,mixture.get_element_num(),mixture.density]
            f.write(format_line(mixture_descrip))
            for compo in mixture.elements.all():
                element_info=[' ',compo.wims_element.element_name,compo.weight_percent/100 if compo.weight_percent else compo.element_number]
                f.write(format_line(element_info))
        f.write('\n')
               
        f.close()
        
    def __str__(self):
        return self.name

class BasicElementComposition(BaseModel):
    basic_material=models.ForeignKey(BasicMaterial,related_name='elements')
    wims_element=models.ForeignKey(WmisElementData,)
    weight_percent=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",blank=True,null=True,)
    element_number=models.PositiveSmallIntegerField(blank=True,null=True)
    class Meta:
        db_table='basic_element_composition'
        order_with_respect_to='basic_material'
    def clean(self):
        if self.weight_percent and self.element_number:
            raise ValidationError({'weight_percent':_('weight_percent and element_number are not compatible'), 
                                 'element_number':_('weight_percent and element_number are not compatible'),                          
            })  
        elif (not self.weight_percent) and (not self.element_number):
            raise ValidationError({'weight_percent':_('you should input at least weight_percent or element_number'), 
                                 'element_number':_('you should input at least weight_percent or element_number'),                          
            })
            
    def __str__(self):
        return '{} {}'.format(self.basic_material, self.wims_element)

#describe material information
class Material(BaseModel):
    nameCH=models.CharField(max_length=40,blank=True)
    nameEN=models.CharField(max_length=40,blank=True)
    bpr_B10=models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),],help_text=r"mg/cm",blank=True,null=True)
    enrichment=models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),],help_text=r"U235:%",blank=True,null=True)
    weight_composition=models.ManyToManyField(BasicMaterial,through='MaterialWeightComposition',)
    volume_composition=models.ManyToManyField('self',through='MaterialVolumeComposition',symmetrical=False)
    symbolic=models.BooleanField(default=False)
    class Meta:
     
        db_table='material'
        verbose_name='Material repository'
        verbose_name_plural='Material repository'
    
            
    def get_prerobin_identifier(self,fuel_index=None):
       
        if fuel_index:
            return 'FUEL_'+str(fuel_index)
        elif self.HOMO:
            return 'HOMO_'+str(self.pk)
        else:
            return self.nameEN
    @property
    def HOMO(self):
        return True if self.volume_composition.exists() else False
        
    def get_density(self,fuel_pellet=None):
        if not self.symbolic:
            #factor only apply to fuel
            factor=fuel_pellet.factor if (fuel_pellet and self.enrichment) else None
            compo=self.weight_mixtures.all()
            result=100/sum(item.percent/item.basic_material.density for item in compo)
            return round(factor*result,5) if factor else round(result,5) 
        else:
            return None
        
    def generate_base_mat(self,fuel_pellet=None,fuel_index=None):
        if self.symbolic:
            return 
        result={'ID':self.get_prerobin_identifier(fuel_index)}
        #HOMO_
        if self.HOMO:
            compo=self.volume_mixtures.all()
            composition_ID_lst=[item.material.get_prerobin_identifier() for item in compo]
            volume_percent_lst=[str(item.percent) for item in compo]
            result['homogenized_mat']=','.join(composition_ID_lst)
            result['volume_percent']=','.join(volume_percent_lst)
            return  result
        
        if self.bpr_B10 is None:
            result['density']=self.get_density(fuel_pellet)
            compo=self.weight_mixtures.all()
            composition_ID_lst=[item.basic_material.get_name(self.enrichment) for item in compo]
            weight_percent_lst=[str(item.percent) for item in compo]
            result['composition_ID']=','.join(composition_ID_lst)
            result['weight_percent']=','.join(weight_percent_lst)
        else:
            result['bpr_B10']=self.bpr_B10
            compo=self.weight_mixtures.all()
            composition_ID_lst=[item.basic_material.name for item in compo]
            weight_percent_lst=[str(item.percent) for item in compo]
            result['composition_ID']=','.join(composition_ID_lst)
            result['weight_percent']=','.join(weight_percent_lst)
        
        return  result  
    
    def generate_base_mat_xml(self,fuel_pellet=None):
        base_mat=self.generate_base_mat(fuel_pellet)
        doc = minidom.Document()
        base_mat_xml=doc.createElement('base_mat')
        for key,value in base_mat.items():
            key_xml=doc.createElement(str(key))
            key_xml.appendChild(doc.createTextNode(str(value)))
            base_mat_xml.appendChild(key_xml)
        return base_mat_xml
        
    @classmethod
    def generate_material_databank_xml(cls,base_mat_lst):
        #f=open("material_databank.xml",'w')
        doc = minidom.Document()
        material_databank_xml=doc.createElement('material_databank')
#         base_mat_lst=cls.generate_base_mat_lst()
        for base_mat in  base_mat_lst:
            if base_mat:
                base_mat_xml=doc.createElement('base_mat')
                for key,value in base_mat.items():
                    key_xml=doc.createElement(str(key))
                    key_xml.appendChild(doc.createTextNode(str(value)))
                    base_mat_xml.appendChild(key_xml)
                material_databank_xml.appendChild(base_mat_xml)
        doc.appendChild(material_databank_xml) 
        #doc.writexml(f, indent="  ", addindent="  ", newl="\n") 
        #f.close()     
        return material_databank_xml  
        
            
    def __str__(self):
        if self.nameEN:
            return self.nameEN
        elif self.enrichment:
            return "UO2_"+str(self.enrichment)
        else:
            return self.get_prerobin_identifier()
        
class MaterialWeightComposition(BaseModel):
    mixture=models.ForeignKey(Material,related_name='weight_mixtures',)
    basic_material=models.ForeignKey(BasicMaterial)
    percent=models.DecimalField(max_digits=8, decimal_places=5,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    class Meta:
        db_table='material_weight_composition'
        verbose_name='Weight Composition'
        verbose_name_plural='Weight Composition'
             
    def __str__(self):
        return "{} {}".format(self.mixture, self.basic_material)   
    
class MaterialVolumeComposition(BaseModel):
    mixture=models.ForeignKey(Material,related_name='volume_mixtures',)
    material=models.ForeignKey(Material)
    percent=models.DecimalField(max_digits=8, decimal_places=5,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    class Meta:
        db_table='material_volume_composition'
        verbose_name='Volume Composition'
        verbose_name_plural='Volume Composition'
             
    def __str__(self):
        return "{} {}".format(self.mixture, self.material) 
    

    
class Vendor(BaseModel):
    TYPE_CHOICES=(
        ('Designer','Designer'),
        ('Manufacturer','Manufacturer'),
        ('Material','Material'),
    )
    nameCH=models.CharField(max_length=40)
    abbrCH=models.CharField(max_length=40)
    nameEN=models.CharField(max_length=40)
    abbrEN=models.CharField(max_length=40)
    type=models.CharField(max_length=12, choices=TYPE_CHOICES,default='Designer')
    
    class Meta:
        db_table='vendor'
        
    def __str__(self):
        return self.abbrCH
    
#################################################
#nuclear power plant basic information 
#################################################

class Plant(BaseModel):
    nameCH=models.CharField(max_length=40)
    abbrCH=models.CharField(max_length=40)
    nameEN=models.CharField(max_length=40)
    abbrEN=models.CharField(max_length=40)
    reactor_model = models.ForeignKey('ReactorModel')
    class Meta:
        db_table='plant'
        
    @property
    def plant_dir(self):
        media_root=settings.MEDIA_ROOT
        plant_dir=os.path.join(media_root, 'pre_robin',self.abbrEN)
        return plant_dir
    
        
    def __str__(self):
        return self.abbrEN  
    
def get_drwm_file_path(instance,filename):
    
    return 'pre_robin/{}/{}'.format(instance.name,filename)
    
    
class ReactorModel(BaseModel):
    MODEL_CHOICES=(
        ('CP600','CP600'),
        ('CP300','CP300'),
        ('M310','M310'),
        ('CAP1000','CAP1000'),
        ('AP1000','AP1000'),
    )
    GENERATION_CHOICES = (
        ('2', '2'),
        ('2+', '2+'),
        ('3', '3'),
    )

    TYPE_CHOICES = (
        ('PWR', 'PWR'),
        ('BWR', 'BWR'),
    )

    GEOMETRY_CHOICES = (
        ('Cartesian', 'Cartesian'),
        ('Hexagonal', 'Hexagonal'),
    )
    
    SYMBOL_CHOICES = (
        ('Number', 'Number'),
        ('Letter', 'Letter'),
    )
    DIRECTION_CHOICES = (
        ('E','East'),
        ('S', 'South'),
        ('W','West'),
        ('N', 'North'),
    )
    DRWM_FILE_FORMAT_CHOICES=(
        (0,'Decimal'),
        (1,'Binary'),
    )
    name = models.CharField(max_length=50,choices=MODEL_CHOICES)
    generation = models.CharField(max_length=2, choices=GENERATION_CHOICES)
    reactor_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    geometry_type = models.CharField(max_length=9, choices=GEOMETRY_CHOICES)
    dimension=models.PositiveSmallIntegerField(default=15,help_text='the maximum assembly number per dimension allowed')
    row_symbol = models.CharField(max_length=6, choices=SYMBOL_CHOICES)
    column_symbol = models.CharField(max_length=6, choices=SYMBOL_CHOICES)
    letter_order=models.CharField(max_length=32,default='A B C D E F G H J K L M N')
    num_loops = models.PositiveSmallIntegerField(blank=True,null=True)
    fuel_pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',null=True)
    core_equivalent_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    active_height= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    vendor = models.ForeignKey(Vendor,blank=True,null=True)  
    thermal_couple_position=models.ManyToManyField('ReactorPosition',related_name='thermal_couple_position',db_table='thermal_couple_map',blank=True,)
    incore_instrument_position=models.ManyToManyField('ReactorPosition',related_name='incore_instrument_position',db_table='incore_instrument_map',blank=True,)
    fuel_temperature=models.PositiveSmallIntegerField(default=903,help_text='K')
    moderator_temperature=models.PositiveSmallIntegerField(default=577,help_text='K')
    control_rod_step_size=models.DecimalField(max_digits=7,decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',default=1.58310)
    default_step=models.PositiveSmallIntegerField(default=225)
    max_step=models.PositiveSmallIntegerField(default=228)
    set_zero_to_direction=models.CharField(max_length=1, choices=DIRECTION_CHOICES,default='E')
    clockwise_increase=models.BooleanField(default=True)
    drwm_file_format=models.SmallIntegerField(default=1,choices=DRWM_FILE_FORMAT_CHOICES)
    drwm_file=models.FileField(upload_to=get_drwm_file_path,blank=True,null=True)
    class Meta:
        db_table = 'reactor_model'
        
    @property
    def control_rod_clusters(self):
        return ControlRodCluster.objects.filter(control_rod_assembly_type__reactor_model=self)
        
    @property
    def reactor_model_dir(self):
        return os.path.join(PRE_ROBIN_PATH,self.name)
    
    @property
    def idyll_dir(self):
        return os.path.join(self.reactor_model_dir,'IDYLL')
    @property
    def task_dir(self):
        return os.path.join(self.reactor_model_dir,'task')
    
    @property    
    def base_component_path(self):
        return os.path.join(self.reactor_model_dir,'base_component.xml')
    
    @property
    def middle(self):
        return math.ceil(self.dimension/2)
    

    def in_core(self,row,col):
        return self.positions.filter(row=row,column=col).exists()
    
    
    def in_outer(self,row,col):
        if self.in_core(row-1, col) and self.in_core(row+1, col) and self.in_core(row, col-1) and self.in_core(row, col+1):
            return False
        else:
            return True
    
    @property
    def start_pos(self):
        '''
        reflect computation start position
        '''
        dimension=self.dimension
        middle=self.middle
        return (dimension+1,middle)
    
    @property
    def end_pos(self):
        '''
        reflect computation start position
        '''
        quarter_pos=self.quarter_pos
        return (quarter_pos+1,quarter_pos+1)
    
    def next(self,current_pos):
        '''
        only apply to the 1/8 core
        '''
        
        end_pos=self.end_pos
        #reach the end
        if current_pos==end_pos:
            return None
        row=current_pos[0]
        col=current_pos[1]
        up_in_core=self.in_core(row-1,col)
        if up_in_core:
            return (row,col+1)
        else:
            return (row-1,col)
    @property
    def quarter_pos(self):
        '''
        the lower right corner position

        '''
        dimension=self.dimension
        for i in range(dimension,0,-1):
            if self.in_core(i, i):
                return i
        
        
   
        
    
    def generate_pos_index(self,row,col,outer=True):
        '''
        only apply for the lower right part of the core(1/8 core)
        return ((inner index),(outer index))
        '''
        
        left_in_core=self.in_core(row,col-1)
        up_in_core=self.in_core(row-1,col)
        
        if self.in_core(row,col):
            return None
        #locate at the quarter line
        elif row==col:
            if up_in_core:
                result=([6,5,6],[8,])
            else:
                result= ([9,],[10,12,10]) 
        #in the 1/8 core
        else:
            
            if left_in_core and up_in_core:
                result= ([6,5,7],[8,])
            elif left_in_core or up_in_core:
                result=([3,3],[4,4])
            else:
                result=([9,],[10,12,11])
        return result[int(outer)]
    
    def generate_reflector_line(self):
        line=[]
        start_pos=self.start_pos            
        current_pos=start_pos
        while current_pos:
            line.append(current_pos)
            current_pos=self.next(current_pos)
        return line
    
    def generate_reflector_index(self,outer=True):
        #consider AP1000 seperately
        if self.name=="AP1000":
            if outer:
                return [12,12,12,17,18,17,15,12,12,17,18,17,15,17,18,17,15]
            else:
                return [11,11,11,16,14,13,14,11,11,16,14,13,14,16,14,13]
        line=self.generate_reflector_line()
        index=[]
        for pos in line:
            row=pos[0]
            col=pos[1]
            pos_index=self.generate_pos_index(row,col,outer)
            index +=pos_index
        index.pop(0)
        quarter_pos=self.quarter_pos
        if self.in_outer(quarter_pos, quarter_pos):
            if outer:
                index.pop(-1)
        else:
            if not outer:
                index.pop(-1)
                
        return index
    
    def generate_reflector_model_xml(self,model_type):
        if model_type=='BR1':
            num_fuel_assembly=1
            num_edit_node=16
        elif model_type=='BR2':
            num_fuel_assembly=3
            num_edit_node=16
        elif model_type=='BR3':
            num_fuel_assembly=2
            num_edit_node=16
        elif model_type=='BR_BOT':
            num_fuel_assembly=2
            num_edit_node=4
        elif model_type=='BR_TOP':
            num_fuel_assembly=2
            num_edit_node=16
            
        doc=minidom.Document()
        reflector_model_xml=doc.createElement('reflector_model')
        num_fuel_assembly_xml=doc.createElement('num_fuel_assembly')
        num_fuel_assembly_xml.appendChild(doc.createTextNode(str(num_fuel_assembly)))
        reflector_model_xml.appendChild(num_fuel_assembly_xml)
        
        core_baffle=self.corebaffle
        material_thickness_lst=map(str,core_baffle.get_material_thickness_lst(model_type))
        material_ID_lst=core_baffle.get_material_ID_lst(model_type)
        
        material_thickness_xml=doc.createElement('material_thickness')
        
        material_thickness_xml.appendChild(doc.createTextNode(",".join(material_thickness_lst)))
        reflector_model_xml.appendChild(material_thickness_xml)
        
        material_ID_xml=doc.createElement('material_ID')
        material_ID_xml.appendChild(doc.createTextNode(",".join(material_ID_lst)))
        reflector_model_xml.appendChild(material_ID_xml)
        
        num_edit_node_xml=doc.createElement('num_edit_node')
        num_edit_node_xml.appendChild(doc.createTextNode(str(num_edit_node)))
        reflector_model_xml.appendChild(num_edit_node_xml)
        return reflector_model_xml
    
    def get_reflector_material_lst(self):
        material_set=set()
        core_baffle=self.corebaffle
        radial_material=core_baffle.material
        material_set.add(radial_material)
        bottom_material=core_baffle.bottom_material
        material_set.add(bottom_material)
        top_material=core_baffle.top_material
        material_set.add(top_material)
        for material in [radial_material,bottom_material,top_material]:
            if material.volume_composition.exists():
                for item in material.volume_composition.all():
                    if not item.symbolic:
                        material_set.add(item)
        material_lst=[]
        for item in material_set:
            if item.HOMO:
                material_lst.append(item)
            else:
                material_lst.insert(0, item)
        return material_lst
    
    def __str__(self):
        return '{}'.format(self.name)  
    
  

class ReactorPosition(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel,related_name='positions',related_query_name='position')
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    control_rod_cluster=models.ForeignKey('ControlRodCluster',related_name='positions',related_query_name='position',blank=True,null=True,)
    
    class Meta:
        db_table='reactor_position'
        unique_together=('reactor_model','row','column')
        ordering=['row','column']  
    
    def get_rotate_pos(self):
        dimension=self.reactor_model.dimension
        col=self.row
        row=dimension-self.column+1
        return ReactorPosition.objects.get(reactor_model=self.reactor_model,row=row,column=col)
        
    def get_quadrant_symbol(self):
        '''
        2|1
        ---
        3|4
        '''
        dimension=self.reactor_model.dimension
        
        if self.row<dimension/2 and self.column<dimension/2+1:
            return 2
        elif self.row<dimension/2+1 and self.column>dimension/2:
            return 1
        elif self.row>dimension/2 and self.column<dimension/2:
            return 3
        else:
            return 4
        
    def in_outermost(self):
        '''
        return True if this position in the outermost of the reactor
        '''
        if self.get_pos_by_delt(-1,0) and self.get_pos_by_delt(0,-1) and self.get_pos_by_delt(0,1) and self.get_pos_by_delt(1,0):
            return False
        return True
  
    def get_pos_by_delt(self,delt_row,delt_col):
        row=self.row
        col=self.column
        new_row=row+delt_row
        new_col=col+delt_col
        try:
            new_position=self.reactor_model.positions.get(row=new_row,column=new_col)
        except:
            new_position=None
        return new_position
    
    def get_outher_pos(self):
        '''
        1 2 3
        4 5 6
        7 8 9
        self is 5
        result order is [1,2,3,4,...]
        '''
        return [self.get_pos_by_delt(0,1),self.get_pos_by_delt(1,0),self.get_pos_by_delt(1,1)]
    
        
    def __str__(self):
        rowSymbol=self.reactor_model.row_symbol
        columnSymbol=self.reactor_model.column_symbol
        #transform the number to letter
        if rowSymbol=='Letter' and columnSymbol=='Number':
            if self.row<=8:
                rowRpr=chr(self.row+64)
            else:
                rowRpr=chr(self.row+65)
            
            columnRpr=str(self.column).zfill(2)    
            return '{}{}'.format(rowRpr,columnRpr)    
        else:
            rowRpr=str(self.row).zfill(2)
            column_max=self.reactor_model.positions.aggregate(Max('column'))['column__max']
            index=66+column_max-self.column
            #kick 'Q'=81
            if index==80:
                columnRpr=chr(index+2)
            #kick 'O'=79
            elif index==79:
                columnRpr=chr(index+1)
            #kick 'I'
            elif index>73:
                columnRpr=chr(index)
            else:
                columnRpr=chr(index-1)
        
            return '{}{}'.format(columnRpr,rowRpr)

#################################################
#nuclear power plant equipment information
#################################################

class CoreBarrel(BaseModel):
    reactor_model =models.OneToOneField(ReactorModel)
    outer_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material = models.ForeignKey(Material)
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='core_barrel'
        
    def __str__(self):
        return "{}'s core barrel".format(self.reactor_model)
        
class CoreUpperPlate(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:Kg')
    material = models.ForeignKey(Material)
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='core_upper_plate'
    
    def __str__(self):
        return "{}'s core upper plate".format(self.reactor_model)
    
class CoreLowerPlate(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:Kg')
    material = models.ForeignKey(Material)
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='core_lower_plate'
    
    def __str__(self):
        return "{}'s core lower plate".format(self.reactor_model)
        
    
class ThermalShield(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel)
    height =models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm') 
    outer_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    angle=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0),MaxValueValidator(360)],help_text='unit:degree')
    loc_height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    loc_theta=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0),MaxValueValidator(360)],help_text='unit:degree')
    gap_to_barrel=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material = models.ForeignKey(Material)
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='thermal_shield'
    
    def __str__(self):
        return "{}'s {} thermal shield".format(self.reactor_model, self.id)
    
class PressureVessel(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    outer_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weld_thickness = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    base_material = models.ForeignKey(Material,related_name='pressure_vessel_base')
    weld_material = models.ForeignKey(Material,related_name='pressure_vessel_weld')
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='pressure_vessel'
    
    def __str__(self):
        return "{}'s pressure vessel".format(self.reactor_model)

class PressureVesselInsulation(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    outer_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material = models.ForeignKey(Material)
    vendor = models.ForeignKey(Vendor)
    
    class Meta:
        db_table='pressure_vessel_insulation'
    
    def __str__(self):
        return "{}'s pressure vessel insulation".format(self.reactor_model)
    

def bottom_material_default():
    mod=Material.objects.get(nameEN='MOD')
    fe=Material.objects.get(nameEN='Fe')
    obj= Material.objects.filter(volume_mixtures__material=mod).filter(volume_mixtures__percent=10).filter(volume_mixtures__material=fe).filter(volume_mixtures__percent=90).first()
    return obj.pk
def top_material_default():
    mod=Material.objects.get(nameEN='MOD')
    fe=Material.objects.get(nameEN='Fe')
    obj= Material.objects.filter(volume_mixtures__material=mod).filter(volume_mixtures__percent=30).filter(volume_mixtures__material=fe).filter(volume_mixtures__percent=58).first()
    return obj.pk
class CoreBaffle(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    gap_to_fuel=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    outer_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    material = models.ForeignKey(Material)
    thickness= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:Kg',blank=True,null=True)
    vendor = models.ForeignKey(Vendor,blank=True,null=True)
    bottom_gap=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',default=3.112)
    bottom_thickness= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',default=7)
    bottom_material=models.ForeignKey(Material,related_name='bottom_core_baffels',default=bottom_material_default)
    top_material=models.ForeignKey(Material,related_name='top_core_baffels',default=top_material_default)
    class Meta:
        db_table='core_baffle'
        
    def get_material_thickness_lst(self,model_type):
        if model_type in ['BR1','BR2','BR3']:
            return [self.gap_to_fuel,self.thickness]
        else:
            return [self.bottom_gap,self.bottom_thickness]
    
            
    def get_material_ID_lst(self,model_type):
        if model_type in ['BR1','BR2','BR3']:
            return ['MOD',self.material.get_prerobin_identifier(),'MOD']
        elif model_type=='BR_BOT':
            return ['MOD',self.bottom_material.get_prerobin_identifier(),'MOD']
        elif model_type=='BR_TOP':
            return [self.top_material.get_prerobin_identifier()]*3
    
    def __str__(self):
        return "{}'s core baffle".format(self.reactor_model)

#rip plate table is associate with core baffle table    
class RipPlate(BaseModel):
    core_baffle=models.OneToOneField(ReactorModel)
    height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    thickness=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    width= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    material = models.ForeignKey(Material)
    
    class Meta:
        db_table='rip_plate'
    
    def __str__(self):
        return "{}'s rip plate".format(self.core_baffle)


#################################################
#nuclear power plant operation information 
#################################################

class UnitParameter(BaseModel):
    plant = models.ForeignKey(Plant,related_name='units')
    unit = models.PositiveSmallIntegerField()
    #reactor_model = models.ForeignKey(ReactorModel)
    electric_power = models.DecimalField(max_digits=10, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:MW')
    thermal_power = models.DecimalField(max_digits=10, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:MW')
    heat_fraction_in_fuel = models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    primary_system_pressure= models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:MPa')
    ave_linear_power_density= models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:KW/m')
    ave_vol_power_density = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:KW/L', blank=True, null=True)
    ave_mass_power_density = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:W/g (fuel)')
    best_estimated_cool_vol_flow_rate = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:m3/h', blank=True, null=True)
    best_estimated_cool_mass_flow_rate = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:kg/h', null=True)
    coolant_volume=models.DecimalField(max_digits=20, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:m3', null=True)
    bypass_flow_fraction = models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%", blank=True, null=True)
    cold_state_cool_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    HZP_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    HFP_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    HFP_core_ave_cool_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    mid_power_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    num_signal=models.PositiveSmallIntegerField(default=1)
    num_dsf=models.PositiveSmallIntegerField(default=1)
#     boron_density=models.PositiveSmallIntegerField(default=500,help_text='ppm')
#     fuel_temperature=models.PositiveSmallIntegerField(default=903,help_text='K')
#     moderator_temperature=models.PositiveSmallIntegerField(default=577,help_text='K')
    class Meta:
        db_table = 'unit_parameter'
        unique_together = ('plant', 'unit')
        
    @property    
    def reactor_model(self):
        return self.plant.reactor_model
    
    @property
    def unit_dir(self):
        plant=self.plant
        return os.path.join(plant.plant_dir,'unit'+str(self.unit))
    
    
    @property
    def fuel_temperature(self):
        return self.reactor_model.fuel_temperature
    
    @property
    def moderator_temperature(self):
        return self.reactor_model.moderator_temperature
    
    
    @property     
    def depletion_state_lst(self):
        primary_system_pressure=self.primary_system_pressure
        ave_mass_power_density=self.ave_mass_power_density
        fuel_temperature=self.fuel_temperature
        moderator_temperature=self.moderator_temperature
        return [primary_system_pressure,fuel_temperature,moderator_temperature,ave_mass_power_density]
#     @property    
#     def base_component_path(self):
#         plant=self.plant
#         base_component_path=os.path.join(plant.plant_dir,'base_component.xml')
#         if os.path.isfile(base_component_path):
#             return base_component_path
    
    @property
    def base_core_path(self):
        unit_dir=self.unit_dir
        base_core_path=os.path.join(unit_dir,'base_core.xml')
        if os.path.isfile(base_core_path):
            return base_core_path
        
        
    @property
    def loading_pattern_path(self):
        unit_dir=self.unit_dir
        loading_pattern_path=os.path.join(unit_dir,'loading_pattern.xml')
        if os.path.isfile(loading_pattern_path):
            return loading_pattern_path
        
    def duplicate(self,plant,unit_num):
        self.pk=None
        self.plant=plant
        self.unit=unit_num
        self.save()
        
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
        
    def get_current_cycle(self):
        result_cycle=Cycle.get_max_cycle_by_unit(self) 
        while result_cycle:
            if result_cycle.loading_patterns.all():
                return result_cycle
            result_cycle=result_cycle.get_pre_cycle()
    get_current_cycle.short_description='current cycle' 
    
    def generate_base_fuel_set(self):
        cycles=self.cycles.all()  
        base_fuel_set=set()
        for cycle in cycles:
            base_fuel_set.update(cycle.generate_base_fuel_set())
        return base_fuel_set
    
    def generate_drwm_imp_file_xml(self):
        doc=minidom.Document()
        drwm_imp_file_xml=doc.createElement('drwm_imp_file')
        fmt=self.reactor_model.drwm_file_format
        drwm_file_path=self.reactor_model.drwm_file.path
        nsignal=self.num_signal
        ndsf=self.num_dsf
        
        drwm_imp_file_xml.setAttribute('fmt', str(fmt))
        drwm_imp_file_xml.setAttribute('nsignal', str(nsignal))
        drwm_imp_file_xml.setAttribute('ndsf', str(ndsf))
        drwm_imp_file_xml.appendChild(doc.createTextNode(drwm_file_path))
        
        return drwm_imp_file_xml
        
    def __str__(self):
        return '{} U{}'.format(self.plant, self.unit)
 
class Cycle(BaseModel):
    unit=models.ForeignKey(UnitParameter,related_name='cycles')
    cycle = models.PositiveSmallIntegerField()
    starting_date = models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True, null=True)
    shutdown_date = models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True, null=True)
    cycle_length = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:EFPD',blank=True, null=True) 
    num_unplanned_shutdowns = models.PositiveSmallIntegerField(blank=True, null=True)
    num_periodical_tests = models.PositiveSmallIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'cycle'
        unique_together = ('cycle', 'unit')
        verbose_name='Operation cycle'
        
    @classmethod
    def get_max_cycle_by_unit(cls,unit):
        return cls.objects.filter(unit=unit).order_by('cycle').last()
        
    #validating objects(clean_fields->clean->validate_unique)
    def clean(self):
        cycle_num=self.cycle
        if cycle_num!=1:
            pre_cycle=self.get_pre_cycle()
            if not pre_cycle:
                raise ValidationError({'cycle':_('the cycle number is not consistent')})
    

    def get_pre_cycle(self):
        try:
            pre_cycle=Cycle.objects.get(unit=self.unit,cycle=self.cycle-1)
            return pre_cycle
        except:
            return None
        
    def get_nth_cycle(self,n):
        try:
            n_cycle=Cycle.objects.get(unit=self.unit,cycle=self.cycle+n)
            return n_cycle
        except:
            return None
        
    def get_loading_pattern_by_pos(self,row,column):
        reactor_model=self.unit.reactor_model
        reactor_position=reactor_model.positions.get(row=row,column=column)
        try:
            falp=self.loading_patterns.get(reactor_position=reactor_position)
            return falp
        except:
            return None
        
    def generate_loading_pattern_xml(self):
        unit=self.unit
        plant=unit.plant
        #start xml 
        doc = minidom.Document()
        loading_pattern_xml = doc.createElement("loading_pattern")
        loading_pattern_xml.setAttribute("cycle_num",str(self.cycle))
        loading_pattern_xml.setAttribute("unit_num",str(unit.unit))
        loading_pattern_xml.setAttribute("plant_name",plant.abbrEN)
        doc.appendChild(loading_pattern_xml)
        
        loading_patterns=self.loading_patterns.all() 
        
        for loading_pattern in loading_patterns:
            reactor_position=loading_pattern.reactor_position
            row=reactor_position.row
            column=reactor_position.column
            position_xml=doc.createElement('position')
            position_xml.setAttribute('row', str(row))
            position_xml.setAttribute('column', str(column))
            #rotation
            rotation_degree=loading_pattern.rotation_degree
            position_xml.setAttribute('rotation', str(rotation_degree))
            #fuel assembly
            fuel_assembly=loading_pattern.fuel_assembly
            fuel_assembly_xml=fuel_assembly.generate_fuel_assembly_xml(loading_pattern)
            position_xml.appendChild(fuel_assembly_xml)
            #burnable poison assembly
            burnable_poison_assembly=loading_pattern.burnable_poison_assembly
            if burnable_poison_assembly:
                burnable_poison_assembly_xml=burnable_poison_assembly.generate_burnable_poison_assembly_xml()
                position_xml.appendChild(burnable_poison_assembly_xml)
            #control rod assembly
            cr_out=loading_pattern.cr_out
            if cr_out:
                position_xml.setAttribute("cr_out",'1')
            loading_pattern_xml.appendChild(position_xml)
        f = tempfile.TemporaryFile(mode='w+')
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        return f
    
    @property
    def completed(self):
        return True if self.loading_patterns.exists() else False
    @property
    def loading_pattern_name(self):
        unit=self.unit
        plant=unit.plant
        return "STD_{}_U{}C{}".format(plant.abbrEN, unit.unit,self.cycle)
    
    def refresh_loading_pattern(self):
        if self.completed:
            loading_pattern_name=self.loading_pattern_name
            xml_file=self.generate_loading_pattern_xml() 
            try:
                loading_pattern=self.multipleloadingpattern_set.get(authorized=True)
                try:
                    loading_pattern.xml_file.delete()
                    #send a signal to delete the old file
                    del_fieldfile.send(sender=loading_pattern.__class__,pk=loading_pattern.pk)
                except:
                    pass
                #save the new file
                loading_pattern.xml_file=File(xml_file)
                loading_pattern.save()
            except Exception as e:
                print(e)
                #if not exists,create a new one
                self.multipleloadingpattern_set.create(name=loading_pattern_name,authorized=True,xml_file=File(xml_file),user=User.objects.get(username='admin')) 
            xml_file.close()
        
    def generate_base_fuel_set(self):
        base_fuel_set=set()
        fuel_assembly_loading_patterns=self.loading_patterns.all()
        for fuel_assembly_loading_pattern in fuel_assembly_loading_patterns:
            fuel_assembly_type=fuel_assembly_loading_pattern.fuel_assembly.type
            burnable_poison_assembly=fuel_assembly_loading_pattern.burnable_poison_assembly
            if burnable_poison_assembly:
                burnable_poison_assembly=burnable_poison_assembly.get_symmetry_bpa()
           
            base_fuel_set.add((fuel_assembly_type,burnable_poison_assembly))
        return base_fuel_set
    
    def duplicate_loading_pattern(self,cycle):
        loading_patterns=cycle.loading_patterns.all()
        for loading_pattern in loading_patterns:
            loading_pattern.pk=None
            loading_pattern.cycle=self
            fuel_assembly=FuelAssemblyRepository.objects.create(type=loading_pattern.fuel_assembly.type,unit=self.unit)
            loading_pattern.fuel_assembly=fuel_assembly
            loading_pattern.save()
        
    def __str__(self):
        return '{}C{}'.format(self.unit, self.cycle)
    
class FuelAssemblyLoadingPattern(BaseModel):
    ROTATION_DEGREE_CHOICES=(
        (1,'0'),
        (2,'90'),
        (3,'180'),
        (4,'270'),
    )
    cycle=models.ForeignKey(Cycle,related_name='loading_patterns')
    reactor_position=models.ForeignKey(ReactorPosition)
    fuel_assembly=models.ForeignKey('FuelAssemblyRepository',related_name='cycle_positions',default=1)
    rotation_degree=models.PositiveSmallIntegerField(choices=ROTATION_DEGREE_CHOICES,default=1,help_text='anticlokwise')
    burnable_poison_assembly=models.ForeignKey('BurnablePoisonAssembly',related_name="bpa",blank=True,null=True)
    #control_rod_assembly=models.ForeignKey('ControlRodAssembly',related_name="cra",blank=True,null=True)
    cr_out=models.NullBooleanField()
    class Meta:
        db_table='fuel_assembly_loading_pattern'
        unique_together=(('cycle','reactor_position'),('cycle','fuel_assembly'))
        verbose_name='Incore fuel loading pattern'
        
    def clean(self):
        if self.cycle.unit.reactor_model !=self.reactor_position.reactor_model:
            raise ValidationError({'cycle':_('the cycle and reactor_position are not compatible'),
                                   'reactor_position':_('the cycle and reactor_position are not compatible')
                                   
            })
    
    def get_previous(self):
        fuel_assembly=self.fuel_assembly
        cycle=self.cycle
        try:
            falp=FuelAssemblyLoadingPattern.objects.filter(fuel_assembly=fuel_assembly,cycle__cycle__lt=cycle.cycle,cycle__unit=cycle.unit)
            cycle_max=falp.aggregate(Max('cycle__cycle'))['cycle__cycle__max']
            return falp.get(cycle__cycle=cycle_max)
        except:
            return None
        
    def get_all_previous(self):
        fuel_assembly=self.fuel_assembly
        cycle=self.cycle
        try:
            falp=FuelAssemblyLoadingPattern.objects.filter(fuel_assembly=fuel_assembly,cycle__cycle__lte=cycle.cycle,cycle__unit=cycle.unit)
            lst=[]
            
            for item in falp:
                data="{}-{}-{}".format(item.cycle.cycle,item.reactor_position.row,item.reactor_position.column)
                lst.append(data)
            return lst
        except:
            return None
    
    def if_insert_bpa(self):
        return True if self.burnable_poison_assembly else False
            
    def if_insert_cra(self):
        return True if (self.reactor_position.control_rod_cluster and not self.cr_out) else False
            
    def get_grid(self):
        fuel_assembly=self.fuel_assembly
        grids=fuel_assembly.type.model.grid_positions.all()
        tmp_lst=[]
        for grid in grids:
            tmp=grid.grid.functionality+"("+str(grid.height)+")"
            tmp_lst.append(tmp)
        result='-'.join(tmp_lst)
        return result
      
       
    def __str__(self):
        return '{} {}'.format(self.cycle, self.reactor_position)


#################################################
#fuel assembly information 
#################################################  

class FuelAssemblyModel(BaseModel):
    name=models.CharField(max_length=5)
    active_length=models.DecimalField(max_digits=10, decimal_places=5,default=365.8,validators=[MinValueValidator(0)],help_text='unit:cm')
    side_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],blank=True,null=True, help_text='unit:cm')
    assembly_pitch=models.DecimalField(max_digits=7, decimal_places=4,validators=[MinValueValidator(0)],help_text='unit:cm')
    pin_pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    lower_gap=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],blank=True,null=True,help_text='unit:cm')
    upper_gap=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],blank=True,null=True,help_text='unit:cm')
    side_pin_num=models.PositiveSmallIntegerField(default=17)
    licensed_max_discharge_BU =models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='MWd/tU',blank=True,null=True)
    licensed_pin_discharge_BU =models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='MWd/tU',blank=True,null=True)
    vendor=models.ForeignKey(Vendor,blank=True,null=True)
    
    class Meta:
        db_table='fuel_assembly_model'
    
    def get_water_volume(self,active_height):
        total_volume=self.get_active_volume(active_height)
        gt_volume=self.guide_tube.get_active_volume(active_height)
        it_volume=self.guide_tube.get_active_volume(active_height)
        fe_volume=self.fuel_elements.first().claddingtube.get_active_volume(active_height)
        
        positions=self.positions.all()
        gt_num=positions.filter(type="guide").count()
        it_num=positions.filter(type="instrument").count()
        fe_num=positions.filter(type="fuel").count()
        return total_volume-gt_volume*gt_num-it_volume*it_num-fe_volume*fe_num
    
    def get_water_in_guide_tube(self,active_height):
        positions=self.positions.all()
        gt_num=positions.filter(type="guide").count()
        it_num=positions.filter(type="instrument").count()
        gt_volume=self.guide_tube.get_water_volume(active_height)
        return (gt_num+it_num)*gt_volume
    
    def get_wet_frac(self):
        active_height=self.active_length
        water_volume=self.get_water_volume(active_height)
        active_volume=self.get_active_volume(active_height)
        return round(water_volume/active_volume,5)
    
    def get_wet_frac_crin(self,control_rod_type):
        active_height=self.active_length
        water_volume=self.get_water_volume(active_height)
        gt_num=self.positions.filter(type="guide").count()
        cr_volume=control_rod_type.get_active_volume(active_height)
        active_volume=self.get_active_volume(active_height)
        return round((water_volume-gt_num*cr_volume)/active_volume,5)
    
    def get_wet_frac_bpin(self,get_bp_vol):
        '''
        get_bp_vol is function which has one parameter active_height
        '''
        active_height=self.active_length
        water_volume=self.get_water_volume(active_height)
        bp_vol=get_bp_vol(active_height)
        active_volume=self.get_active_volume(active_height)
        return round((water_volume-bp_vol)/active_volume,5)
    
    def get_active_volume(self,active_height):
        assembly_pitch=self.assembly_pitch
        return assembly_pitch*assembly_pitch*active_height
        
    def generate_assembly_model_xml(self,symmetry=8):
        doc = minidom.Document()
        assembly_model_xml=doc.createElement('assembly_model')
        model_ID_xml=doc.createElement('model_ID')
        model_ID_xml.appendChild(doc.createTextNode(self.name))
        assembly_model_xml.appendChild(model_ID_xml)
        
        
        grid_xml=doc.createElement('spacer_grid_mat')
        fix_grid=self.grids.first()
        grid_xml.appendChild(doc.createTextNode(fix_grid.sleeve_material.get_prerobin_identifier()))
        assembly_model_xml.appendChild(grid_xml)
          
        symmetry_xml=doc.createElement('symmetry')
        #default 1/8
        symmetry_xml.appendChild(doc.createTextNode(str(symmetry)))
        assembly_model_xml.appendChild(symmetry_xml)
        
        side_num=self.side_pin_num
        num_pin_side_xml=doc.createElement('num_pin_side')
        num_pin_side_xml.appendChild(doc.createTextNode(str(side_num)))
        assembly_model_xml.appendChild(num_pin_side_xml)
        
        pitch_assembly_xml=doc.createElement('pitch_assembly')
        pitch_assembly_xml.appendChild(doc.createTextNode(str(self.assembly_pitch)))
        assembly_model_xml.appendChild(pitch_assembly_xml)
        
        pitch_cell_xml=doc.createElement('pitch_cell')
        pitch_cell_xml.appendChild(doc.createTextNode(str(self.pin_pitch)))
        assembly_model_xml.appendChild(pitch_cell_xml)
        
        return assembly_model_xml
    
    @property
    def total_grid_type_num(self):
        return len(self.get_grid_material_lst())
    
    def get_grid_material_lst(self):
        grids=self.grids.all()
        material_lst=[]
        for grid in grids:
            material=grid.generate_moderator_material()
            if material  not in material_lst:
                material_lst.append(material)
        return material_lst
    
    def distribute_tube(self):
        if self.positions.all().exists():
            return 0
        else:
            side_pin_num=self.side_pin_num
            try:
                base=FuelAssemblyModel.objects.filter(side_pin_num=side_pin_num).exclude(pk=self.pk).first()
                for position in base.positions.all():
                    position.pk=None
                    position.fuel_assembly_model=self
                    position.save()
            except:
                for row in range(1,side_pin_num+1):
                    for col in range(1,side_pin_num+1):
                        FuelAssemblyPosition.objects.create(fuel_assembly_model=self,row=row,column=col)
            
            return self.positions.count()    
               
    def __str__(self):
        return "{}".format(self.name)

class FuelAssemblyType(BaseModel):
    model=models.ForeignKey(FuelAssemblyModel)
    name=models.CharField(max_length=10)
    assembly_enrichment=models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0)],help_text='meaningful only if using the one unique enrichment fuel',blank=True,null=True)
    map=models.ManyToManyField('FuelElementType',through='FuelElementTypePosition')
    symmetry=models.BooleanField(default=True,help_text="satisfy 1/8 symmetry")
    Gd_num=models.PositiveSmallIntegerField(default=0)
    class Meta:
        db_table='fuel_assembly_type'
        
    @property
    def side_pin_num(self):
        return self.model.side_pin_num
    
    def get_rob_pk_dic(self):
        rod_pk_dic={}
        for fet in self.map.all():
            rod_pk=fet.pk
            if rod_pk not in rod_pk_dic:
                rod_pk_dic[rod_pk]=1
            else:
                rod_pk_dic[rod_pk]+=1
        return rod_pk_dic
    
    def get_height_lst(self,fuel=False):
        rods=self.map.all()
        height_set=set()
        for rod in rods:
            rod_set=set(rod.get_height_lst(fuel=fuel))
            height_set=height_set|rod_set
        height_lst=sorted(list(height_set))
        return height_lst
    
    def generate_transection(self,height,fuel=False,pellet=False):
        if self.symmetry:
            rod_positions=self.rod_positions.all()
            transection={}
            for rod_position in rod_positions:
                if rod_position.in_triangle:
                    row=rod_position.row
                    column=rod_position.column
                    #get the fuel element
                    fet=rod_position.fuel_element_type
                    rod_transection_pk=fet.which_transection(height,fuel=fuel,pellet=pellet)
                    #has bpa at this height
                    if rod_transection_pk:
                        transection[(row,column)]=rod_transection_pk
            return transection
        else:
            return None
        
    @property   
    def assembly_name(self):
        return self.model.name
    
    def get_fuel_lst(self,height):
        transection=self.generate_transection(height,fuel=True)
        side_num=self.side_pin_num
        half=int(side_num/2)+1
        fuel_lst=[]
        for row in range(half,side_num+1):
            for col in range(half,row+1):
                pos=(row,col)
                if pos in transection:
                    fuel_lst.append(transection[pos])
                    
                else:
                    fuel_lst.append(0)
                    
        return  fuel_lst 
  
    def generate_fuel_map_xml(self,height):
        transection=self.generate_transection(height=height,fuel=True)
        doc=minidom.Document()
        side_num=self.side_pin_num
        half=int(side_num/2)+1
        
        #fuel map
        fuel_map='\n'
        for row in range(half,side_num+1):
            row_lst=[]
            for col in range(half,row+1):
                pos=(row,col)
                if pos in transection:
                    transection_pk=transection[pos]
                    fuel_str=str(transection_pk)
                else:
                    fuel_str='0'
                    
                row_lst.append(fuel_str)
                
            fuel_map +=('  '.join(row_lst)+'\n')
        
        fuel_map_xml=doc.createElement('fuel_map')
        fuel_map_xml.appendChild(doc.createTextNode(fuel_map))
        return fuel_map_xml
    
    def get_fuel_element_type(self):
        enrichment=self.assembly_enrichment
        fuel_element_types=FuelElementType.objects.filter(model__fuel_assembly_model=self.model)
        for fuel_element_type in fuel_element_types:
            if fuel_element_type.enrichment==enrichment:
                return fuel_element_type
    def get_other_fet(self):
        fet=self.get_fuel_element_type()
        rod_positions=self.rod_positions.exclude(fuel_element_type=fet)
        if rod_positions.exists():
            return (rod_positions.count(),rod_positions.first().fuel_element_type)
        else:
            return None
            
    def insert_fuel(self):
        '''only available if all fuel element is the same 
        '''
        fuel_element_type=self.get_fuel_element_type()
        positions=self.model.positions.filter(type="fuel")
        num=0
        for position in positions:
            try:
                FuelElementTypePosition.objects.create(fuel_assembly_type=self,fuel_assembly_position=position,fuel_element_type=fuel_element_type)
                num+=1
            except:
                pass
        #insert gd
        if self.Gd_num!=0:
            try:
                fat=FuelAssemblyType.objects.filter(model=self.model,symmetry=self.symmetry,Gd_num=self.Gd_num,).exclude(assembly_enrichment=self.assembly_enrichment).first()
                fet=fat.get_fuel_element_type()
                for rod_position in fat.rod_positions.exclude(fuel_element_type=fet):
                    position=rod_position.fuel_assembly_position
                    gd_fet=rod_position.fuel_element_type
                    rp=self.rod_positions.get(fuel_assembly_position=position)
                    rp.fuel_element_type=gd_fet
                    rp.save()
            except:
                pass
        return num
        
    def __str__(self):
        if self.name:
            return self.name
        if self.Gd_num!=0:
            return "{} {} {} {}Gd".format(self.pk,self.model,self.assembly_enrichment,self.Gd_num)  
        else:
            return "{} {} {}".format(self.pk,self.model,self.assembly_enrichment)
        
    
class FuelAssemblyRepository(BaseModel):
    PN=models.CharField(max_length=50,blank=True,null=True)
    type=models.ForeignKey(FuelAssemblyType)
    batch_number=models.PositiveSmallIntegerField(blank=True,null=True)
    manufacturing_date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True)
    arrival_date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True)
    vendor=models.ForeignKey(Vendor,blank=True,null=True)
    availability=models.BooleanField(default=True)
    broken=models.BooleanField(default=False)
    broken_cycle=models.ForeignKey(Cycle,related_name='broken_assemblies',blank=True,null=True)
    unavailable_cycle=models.ForeignKey(Cycle,related_name='unavailable_assemblies',blank=True,null=True)
    unit=models.ForeignKey(UnitParameter,related_name='fuel_assemblies',null=True)
    
    class Meta:
        db_table='fuel_assembly_repository'
        verbose_name_plural='Fuel assembly repository'
        
    @staticmethod
    def autocomplete_search_fields():
        return ("pk__iexact", "PN__icontains",)
    
    def fresh(self,cycle):
        first_loading_pattern=self.get_first_loading_pattern()
        if first_loading_pattern.cycle==cycle:
            return True
        else:
            return False
    
    @property
    def broken_cycle_num(self):
        if self.broken_cycle:
            return self.broken_cycle.cycle
        
    @property
    def unavailable_cycle_num(self):
        if self.unavailable_cycle:
            return self.unavailable_cycle.cycle
        
    def get_first_loading_pattern(self):
        cycle_positions=self.cycle_positions.all()
        first_loading_pattern=cycle_positions.first()
        for item in cycle_positions:
            if item.cycle.cycle<first_loading_pattern.cycle.cycle:
                first_loading_pattern=item
        return first_loading_pattern
    
    def generate_section_num(self):
        first_loading_pattern=self.get_first_loading_pattern()
        first_cycle=first_loading_pattern.cycle
        
        first_position=first_loading_pattern.reactor_position
        try:
            bpa_pattern=first_cycle.loading_patterns.filter(burnable_poison_assembly__isnull=True,reactor_position=first_position).get()
            bpa=bpa_pattern.burnable_poison_assembly
            bp_num=bpa.get_poison_rod_num()
        except:
            bp_num=0
            
        return (self.type.pk,first_cycle.pk,bp_num)

    
    def set_batch_number(self):
        first_loading_pattern=self.get_first_loading_pattern()
        self.batch_number=first_loading_pattern.cycle.cycle
        self.save()
    
    def get_all_loading_patterns(self):
        cycle_positions=self.cycle_positions.all()
        loading_pattern_lst=["C{} {}".format(item.cycle.cycle,item.reactor_position) for item in cycle_positions]
        return loading_pattern_lst
    get_all_loading_patterns.short_description='all_loading_patterns'
    
    @property
    def plant(self):
        return self.unit.plant
    

    def get_fuel_assembly_status(self):
        loading_patterns=self.cycle_positions.all()
        current_cycle=self.unit.get_current_cycle()
        if loading_patterns:
            if loading_patterns.filter(cycle=current_cycle):
                return 'In core'
            else:
                return 'Spent fuel pool'
        else:
            return 'Fresh'
        
    def generate_fuel_assembly_xml(self,loading_pattern):
        doc = minidom.Document()
        fuel_assembly_xml=doc.createElement('fuel_assembly')
        fuel_assembly_xml.appendChild(doc.createTextNode(str(self.pk)))
        fuel_assembly_type=self.type
        type_pk=fuel_assembly_type.pk
        enrichment=fuel_assembly_type.assembly_enrichment
        name=fuel_assembly_type.model.name
        #first
        first_loading_pattern=self.get_first_loading_pattern()
        reactor_position=first_loading_pattern.reactor_position
        first_cycle=first_loading_pattern.cycle.cycle
        first_row=reactor_position.row
        first_col=reactor_position.column
        #previous
        previous=loading_pattern.get_previous()
        if previous:
            pre_row=previous.reactor_position.row
            pre_col=previous.reactor_position.column
            pre_cycle=previous.cycle.cycle
            fuel_assembly_xml.setAttribute('pre_row',str(pre_row))
            fuel_assembly_xml.setAttribute('pre_col',str(pre_col))
            fuel_assembly_xml.setAttribute('pre_cycle',str(pre_cycle))
        fuel_assembly_xml.setAttribute('name',name)
        fuel_assembly_xml.setAttribute('enrichment',str(enrichment))
        fuel_assembly_xml.setAttribute('type',str(type_pk))
        fuel_assembly_xml.setAttribute('first_row',str(first_row))
        fuel_assembly_xml.setAttribute('first_col',str(first_col))
        fuel_assembly_xml.setAttribute('first_cycle',str(first_cycle))
        return fuel_assembly_xml
        
        
    def __str__(self):
        return "{} {}".format(self.pk, self.type)
    
    
#the position information of fuel assembly     
class FuelAssemblyPosition(BaseModel):
    TYPE_CHOICES=(('fuel','fuel element tube'),
                  ('guide','guide tube'),
                  ('instrument','instrument tube'),
                  )
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='positions')
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    type=models.CharField(max_length=10,choices=TYPE_CHOICES,default='fuel')
    
    class Meta:
        db_table='fuel_assembly_position'
        unique_together=('fuel_assembly_model','row','column')
        verbose_name='Intra-assembly rod pattern'
        
    def generate_quadrant_symbol(self):
        row=self.row
        column=self.column
        side_num=self.fuel_assembly_model.side_pin_num
        return generate_quadrant_symbol(row,column,side_num)
        
    def __str__(self):
        return '{} R{}C{}'.format(self.fuel_assembly_model, self.row,self.column)

class FuelElementTypePosition(BaseModel):
    fuel_assembly_type=models.ForeignKey(FuelAssemblyType,related_name='rod_positions',)
    fuel_assembly_position=models.ForeignKey(FuelAssemblyPosition,limit_choices_to={'type': 'fuel'})
    fuel_element_type=models.ForeignKey('FuelElementType')
    
    class Meta:
        db_table='fuel_element_type_position'
        unique_together=('fuel_assembly_type','fuel_assembly_position')
        verbose_name='Intra-assembly fuel element loading pattern'
        
    @property
    def row(self):
        return self.fuel_assembly_position.row
    
    @property
    def column(self):
        return self.fuel_assembly_position.column
        
    @property
    def in_triangle(self):
        '''to check if this position is in the 1/8 part to be calculated
        1|2
        ---
        3|4
        the lower triangle of quadrant 4
        '''
        side_num=self.fuel_assembly_type.side_pin_num 
        row=self.row
        column=self.column
        return in_triangle(row,column,side_num)
        
    def __str__(self):
        return '{} {}'.format(self.fuel_element_type,self.fuel_assembly_position)
    



class GridPosition(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='grid_positions')
    grid=models.ForeignKey('Grid')
    height= models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm Base on bottom of fuel') 
    
    class Meta:
        db_table='grid_position'
        
    def __str__(self):
        return '{} {}'.format(self.fuel_assembly_model, self.grid)    

#the component of fuel assembly
class Grid(BaseModel):
    FUCTIONALITY_CHOICS=(
                ('blend','blend'),
                ('fix','fix'),
    )
    name=models.CharField(max_length=50)
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='grids')
    sleeve_volume=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm3')
    spring_volume=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm3',blank=True,null=True)
    side_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',blank=True,null=True)
    sleeve_height=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm')
    sleeve_material=models.ForeignKey(Material,related_name='grid_sleeves',related_query_name='grid_sleeve',null=True)
    spring_material=models.ForeignKey(Material,related_name='grid_springs',related_query_name='grid_spring',blank=True,null=True)
    functionality=models.CharField(max_length=5,choices=FUCTIONALITY_CHOICS,default='fix')

    class Meta:
        db_table='grid'
        verbose_name='Fuel grid'
        
    @property
    def type_num(self):
        fuel_assembly_model=self.fuel_assembly_model
        grid_material_lst=fuel_assembly_model.get_grid_material_lst()
        material=self.generate_moderator_material()
        return grid_material_lst.index(material)+1
    
#     @property
#     def grid_material(self):
#         sleeve_material=self.sleeve_material
#         spring_material=self.spring_material
#         if sleeve_material==spring_material:
#             return {sleeve_material:100}
#         else:
#             sleeve_percent=round(self.sleeve_volume/self.grid_volume*100,5)
#             spring_percent=100-sleeve_percent
#             return {sleeve_material:sleeve_percent,spring_material:spring_percent}
    
#     @property
#     def grid_material_ID(self):
#         if self.sleeve_material==self.spring_material:
#             return self.sleeve_material.get_prerobin_identifier()
#         else:
#             return 'HOMO_grid'+str(self.type_num)
        
    @property
    def grid_volume(self):
        return self.sleeve_volume+self.spring_volume if self.spring_volume else self.sleeve_volume
    
    @property   
    def volume_fraction(self):
        grid_volume=self.grid_volume
        assembly_pitch=self.fuel_assembly_model.assembly_pitch
        assembly_volume=assembly_pitch**2*self.sleeve_height
        return round(grid_volume/assembly_volume,5)
    
    @property
    def water_volume(self):
        active_height=self.sleeve_height
        fuel_assembly_model=self.fuel_assembly_model
        water_volume= fuel_assembly_model.get_water_volume(active_height)-self.grid_volume-fuel_assembly_model.get_water_in_guide_tube(active_height)
        return round(water_volume,5)
   
   
    def generate_moderator_material(self):
        water_volume=self.water_volume
        sleeve_volume=self.sleeve_volume
        spring_volume=self.spring_volume if self.spring_volume else Decimal(0)
        total_volume=water_volume+sleeve_volume+spring_volume
        sleeve_percent=round(sleeve_volume/total_volume*100,5)
        spring_percent=round(spring_volume/total_volume*100,5)
        grid_percent=sleeve_percent+spring_percent
        sleeve_material=self.sleeve_material
        spring_material=self.spring_material
        mod_material=Material.objects.get(nameEN='MOD')   
        if (not spring_material) or sleeve_material==spring_material:
            return {sleeve_material.get_prerobin_identifier():grid_percent,mod_material.get_prerobin_identifier():100-grid_percent}
        else:
            return {sleeve_material.get_prerobin_identifier():sleeve_percent,spring_material.get_prerobin_identifier():spring_percent,mod_material.get_prerobin_identifier():100-grid_percent}
        
    @property
    def moderator_material_ID(self):
        return "HOMO_moderator"+str(self.type_num)
    
    def generate_base_mat(self):
        moderator_material_ID=self.moderator_material_ID
        base_mat={'ID':moderator_material_ID}    
        moderator_material=self.generate_moderator_material()
        homgenized_mat_lst=list(moderator_material.keys())
        percent_lst=[str(moderator_material[key]) for key in homgenized_mat_lst]
        base_mat['homogenized_mat']=','.join(homgenized_mat_lst)
        base_mat['volume_percent']=','.join(percent_lst)
        return base_mat
    
    def __str__(self):
        return '{} {}'.format(self.fuel_assembly_model,self.name)

  
class GuideTube(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel,related_name='guide_tube')
    upper_outer_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    upper_inner_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    buffer_outer_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    buffer_inner_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='guide_tube'
        
    def clean(self):
        if self.upper_outer_diameter<=self.upper_inner_diameter:
            raise ValidationError({'upper_outer_diameter':_('the outer_diameter must be bigger'),
                                   'upper_inner_diameter':_('the outer_diameter must be bigger'),
                                   
            })
    
    def get_active_volume(self,active_height):
        outer_radius=self.upper_outer_diameter/2
        inner_radius=self.upper_inner_diameter/2
        return Decimal(math.pi)*(outer_radius**2-inner_radius**2)*active_height
    
    def get_water_volume(self,active_height):
        inner_radius=self.upper_inner_diameter/2
        return Decimal(math.pi)*(inner_radius**2)*active_height
    
    def generate_base_pin_xml(self):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID='GT'
        radii="{},{}".format(self.upper_inner_diameter/2,self.upper_outer_diameter/2)
        mat='MOD,'+self.material.get_prerobin_identifier()
        
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        base_pin_xml.appendChild(ID_xml)
        
        radii_xml=doc.createElement('radii')
        radii_xml.appendChild(doc.createTextNode(radii))
        base_pin_xml.appendChild(radii_xml)
        
        mat_xml=doc.createElement('mat')
        mat_xml.appendChild(doc.createTextNode(mat))
        base_pin_xml.appendChild(mat_xml)
        
        return base_pin_xml
    
    def __str__(self):
        return "{} guid tube".format(self.material)
    
class InstrumentTube(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel,related_name='instrument_tube')
    outer_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='instrument_tube'
        
    def clean(self):
        if self.outer_diameter<=self.inner_diameter:
            raise ValidationError({'outer_diameter':_('the outer_diameter must be bigger'),
                                   'inner_diameter':_('the outer_diameter must be bigger'),
                                   
            })
            
    def get_active_volume(self,active_height):
        outer_radius=self.outer_diameter/2
        return math.pi*outer_radius**2*active_height
        
    def generate_base_pin_xml(self):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID='IT'
        radii="{},{}".format(self.inner_diameter/2,self.outer_diameter/2)
        mat='MOD,'+self.material.get_prerobin_identifier()
        
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        base_pin_xml.appendChild(ID_xml)
        
        radii_xml=doc.createElement('radii')
        radii_xml.appendChild(doc.createTextNode(radii))
        base_pin_xml.appendChild(radii_xml)
        
        mat_xml=doc.createElement('mat')
        mat_xml.appendChild(doc.createTextNode(mat))
        base_pin_xml.appendChild(mat_xml)
        
        return base_pin_xml
        
    def __str__(self):
        return "{}'s instrument tube".format(self.material)
    
class UpperNozzle(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel)
    pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    plate_thickness=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    plate_porosity=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='upper_nozzle'
        
    def __str__(self):
        return "{}'s upper nozzle".format(self.fuel_assembly_model)
    
class LowerNozzle(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel)
    pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    plate_thickness=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    plate_porosity=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='lower_nozzle'
        
    def __str__(self):
        return "{}'s lower nozzle".format(self.fuel_assembly_model)
    
#################################################
#fuel element information 
################################################# 

class FuelElement(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='fuel_elements')
    overall_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    active_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    radius=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    class Meta:
        db_table='fuel_element'
        
    def get_active_volume(self,active_height):
        radius=self.radius
        return Decimal(math.pi)*radius**2*active_height
  
    @property
    def height_lst(self):
        sections=self.sections.all()
        height_lst=[section.bottom_height for section in sections]
        return height_lst
    
    def which_section(self,height):
        '''
        based on the bottom of fuel active part
        0 represents fuel
        '''
            
        height_lst=self.height_lst
        return which_section(height, height_lst)
    
    def which_transection(self,height):
        '''return the material transection pk at this height
        None represents no bpa
        '''
        section_num=self.which_section(height)
        if section_num==0:
            return None
        else:
            section=self.sections.get(section_num=section_num)
            return section.material_transection.pk
            
    def __str__(self):
        return "{} {}".format(self.pk,self.remark)
    
class FuelElementSection(BaseModel):
    '''
    no containing fuel description
    '''
    fuel_element=models.ForeignKey(FuelElement,related_name='sections')
    section_num=models.PositiveSmallIntegerField()
    length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    material_transection=models.ForeignKey('MaterialTransection')
    
    class Meta:
        db_table='fuel_element_section'
        
    @property
    def previous_section(self):
        section_num=self.section_num
        if  section_num==1:
            return None
        else:
            return FuelElementSection.objects.get(fuel_element=self.fuel_element,section_num=section_num-1)
    
    @property
    def bottom_height(self):
        previous_section=self.previous_section
        if previous_section is None:
            bottom_height=Decimal('0')
        else:
            bottom_height =previous_section.length+ previous_section.bottom_height       
        return  bottom_height
    
    @property
    def pin_id(self):
        return self.material_transection.pin_id
    
    def generate_base_pin_xml(self):
        return self.material_transection.generate_base_pin_xml()
        
    def __str__(self):
        return '{} {}'.format(self.pk,self.remark)
    
class MaterialTransection(BaseModel):
    radius=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    radial_map=models.ManyToManyField(Material,through='TransectionMaterial')
    
    class Meta:
        db_table='material_transection'
        
    @property
    def pin_id(self):
        if self.if_fuel:
            return "FUEL_"+str(self.pk)
        elif self.if_control_rod:
            return "CR_"+str(self.pk)
        else:
            return "BP_"+str(self.pk)
#     @property
#     def radius(self):
#         return self.radial_materials.aggregate(Max('radius'))['radius__max']
    
    def get_active_volume(self,active_height):
        radius=self.radius
        return Decimal(math.pi)*radius**2*active_height
    
    @property
    def if_fuel(self):
        materials=self.radial_map.all()
        if "FUEL" in [str(material) for material in materials]:
            return True
        else:
            return False
        
    @property
    def if_control_rod(self):
        if self.control_rod_sections.all().exists():
            return True
        else:
            return False
        
    @property
    def if_bp_rod(self):
        if self.if_control_rod or self.if_fuel:
            return False
        else:
            return True
    @property
    def material_set(self):
        radial_materials=self.radial_materials.all()
        material_set=set()
        for radial_material in radial_materials:
            material_set.add(radial_material.material.pk)
        return material_set
        
    def generate_base_pin_xml(self,guide_tube=None):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID=self.pin_id
        radial_map=self.radial_materials.order_by('radius')
        radii_tup,mat_tup=zip(*[(str(item.radius),item.material.get_prerobin_identifier()) for item in radial_map])
        
        radii_lst=list(radii_tup)
        mat_lst=list(mat_tup)
        #if not fuel,should consider guide tube
        if not self.if_fuel:
            #insert into guide tube
            radii_lst.append(str(guide_tube.upper_inner_diameter/2))
            radii_lst.append(str(guide_tube.upper_outer_diameter/2))
            mat_lst.append('MOD')
            mat_lst.append(guide_tube.material.get_prerobin_identifier())
  
        radii=','.join(radii_lst)
        mat=','.join(mat_lst)
        
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        base_pin_xml.appendChild(ID_xml)
        
        radii_xml=doc.createElement('radii')
        radii_xml.appendChild(doc.createTextNode(radii))
        base_pin_xml.appendChild(radii_xml)
        
        mat_xml=doc.createElement('mat')
        mat_xml.appendChild(doc.createTextNode(mat))
        base_pin_xml.appendChild(mat_xml)
        
        return base_pin_xml
        
    def __str__(self):
        return '{} {}'.format(self.pk,self.remark)
    
class TransectionMaterial(BaseModel):
    transection=models.ForeignKey(MaterialTransection,related_name='radial_materials',)
    layer_num=models.PositiveSmallIntegerField()
    radius=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    class Meta:
        db_table='transection_material'
        
    def __str__(self):
        return '{} {}'.format(self.transection,self.material)
    

class FuelElementType(BaseModel):
    model=models.ForeignKey(FuelElement)
    pellet=models.ManyToManyField('FuelPelletType',through='FuelElementPelletLoadingScheme')
    
    class Meta:
        db_table='fuel_element_type'
        
    def get_height_lst(self,fuel=False):
        if fuel:
            pellet_sections=self.fuel_pellet_map.order_by('section_num')
            height_lst=[pellet_section.bottom_height for pellet_section in pellet_sections]
        else:
            height_lst=self.model.height_lst
            
        return height_lst
    
    def which_section(self,height,fuel=False):
        #convert height to decimal   
        height_lst=self.get_height_lst(fuel)
        return which_section(height,height_lst)
    
    def which_transection(self,height,fuel=False,pellet=False):
        #if fuel return material pk
        #else return material transection object
        if fuel:
            section_num=self.which_section(height=height,fuel=True) 
            pellet_section=self.fuel_pellet_map.get(section_num=section_num)
            fuel_pellet_type=pellet_section.fuel_pellet_type
            if pellet:
                return fuel_pellet_type.model.pk
            else:
                return fuel_pellet_type.material.pk
        else:
            return self.model.which_transection(height)
    
    @property
    def enrichment(self):
        try:
            pellet_pos=self.pellet.get()
            return pellet_pos.enrichment
        except:
            return None
        
    def __str__(self):
        
        return "{} {} {} ".format(self.pk,self.remark,self.enrichment)
    
    
class UpperCap(BaseModel):
    fuel_element_type=models.OneToOneField(FuelElement)
    height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
  
    
    class Meta:
        db_table='upper_cap'
        
    def __str__(self):
        return "{}'s upper cap".format(self.fuel_element_type)
    

class LowerCap(BaseModel):
    fuel_element=models.OneToOneField(FuelElement)
    height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='lower_cap'
        
    def __str__(self):
        return "{}'s lower cap".format(self.fuel_element)
    
class PlenumSpring(BaseModel):
    fuel_element=models.OneToOneField(FuelElement)
    weight=models.DecimalField(max_digits=10, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:g')
    outer_diameter= models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    wire_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='plenum_spring'
        
    def __str__(self):
        return "{}'s plenum spring".format(self.fuel_element)
    
class CladdingTube(BaseModel):
    fuel_element=models.OneToOneField(FuelElement)
    outer_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    roughness= models.DecimalField(max_digits=7, decimal_places=6,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    material=models.ForeignKey(Material)
    
    
    class Meta:
        db_table='cladding_tube'
        
    
    def get_active_volume(self,active_height):
        radius=self.outer_diameter/2
        return Decimal(math.pi)*radius**2*active_height
        
    def __str__(self):
        return "{}'s cladding tube".format(self.fuel_element)
    

#fake fuel element information 
class FakeFuelElementType(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel)
    overall_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    outer_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    pellet_outer_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    pellet_height=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    class Meta:
        db_table='fake_fuel_element_type'
        
    def __str__(self):
        return '{} fake fuel element'.format(self.material)
    


#Fuel Pellet 
class FuelPellet(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel)
    outer_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    inner_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],blank=True,null=True,help_text='unit:cm can be none when hollow')
    length=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    dish_volume_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    chamfer_volume_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    #dish_depth=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #dish_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #roughness=models.DecimalField(max_digits=7, decimal_places=6,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #nominal_density=models.DecimalField(max_digits=8, decimal_places=5,validators=[MinValueValidator(0)],help_text=r"unit:g/cm3")
    nominal_density_percent=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",default=95) 
    #uncertainty_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",blank=True,null=True)  
    coating_thickness=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    coating_material=models.ForeignKey(Material,related_name='fuel_pellet_coating',blank=True,null=True)
    
    class Meta:
        db_table='fuel_pellet'
    @property
    def hollow_factor(self):
        if self.inner_diameter is not None:
            return 1-(self.inner_diameter/self.outer_diameter)**2
        return Decimal(1)
        
    @property    
    def factor(self):
        return (100-self.dish_volume_percentage-self.chamfer_volume_percentage)/100*(self.nominal_density_percent/100)*self.hollow_factor
    
    def __str__(self):
        return '{} {} pellet'.format(self.pk,self.remark)

class FuelPelletType(BaseModel):
    model=models.ForeignKey(FuelPellet)
    material=models.ForeignKey(Material,related_name='fuel_pellet_material',limit_choices_to={'enrichment__isnull':False})
    
    class Meta:
        db_table='fuel_pellet_type'
        
    @property
    def enrichment(self):
        return self.material.enrichment
    
    def generate_base_mat(self):
        base_mat=self.material.generate_base_mat(self.model)
        return base_mat
    
    @classmethod
    def generate_base_mat_lst(cls):
        objs=cls.objects.all()
        base_mat_lst=[]
        for obj in objs:
            base_mat=obj.generate_base_mat()
            base_mat_lst.append(base_mat)
            
        return base_mat_lst
        
    def __str__(self):
        return '{} {}'.format(self.pk,self.remark)
    
    
class FuelElementPelletLoadingScheme(BaseModel):
    fuel_element_type=models.ForeignKey(FuelElementType,related_name='fuel_pellet_map')
    section_num=models.PositiveSmallIntegerField()
    fuel_pellet_type=models.ForeignKey(FuelPelletType)
    length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)])
    
    class Meta:
        db_table='fuel_element_pellet_loading_scheme'
        
    @property
    def previous_section(self):
        section_num=self.section_num
        if  section_num==1:
            return None
        else:
            return FuelElementPelletLoadingScheme.objects.get(fuel_element_type=self.fuel_element_type,section_num=section_num-1)
    
    @property
    def bottom_height(self):
        previous_section=self.previous_section
        if previous_section is None:
            bottom_height=Decimal('0')
        else:
            bottom_height =previous_section.length+ previous_section.bottom_height       
        return  bottom_height
    
        
    def __str__(self):
        return '{} {} {}'.format(self.fuel_element_type, self.section_num,self.fuel_pellet_type)
    

    
#################################################
#component assembly information 
#################################################    

####################################################################################################################################
#the following five models describe all the component rod type
class ControlRodType(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel,related_name='control_rod_types',blank=True,null=True)
    active_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)  
    black=models.BooleanField(default=True)
    radius=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    class Meta:
        db_table='control_rod_type'
        verbose_name='Control rod'
    
    
    def get_active_volume(self,active_height):
        radius=self.radius
        return Decimal(math.pi)*radius**2*active_height
        
    @property
    def height_lst(self):
        sections=self.sections.all()
        height_lst=[section.bottom_height for section in sections]
        return height_lst
    
    def which_section(self,height):
        #convert height to decimal
        if type(height)==Decimal:
            pass
        else:
            height=Decimal(str(height))
            
        height_lst=self.height_lst
        for i in range(len(height_lst)):
            if height_lst[i]>height:
                return i
            elif height_lst[i]==height:
                return i+1
            
        return len(height_lst) 
    
    def which_transection(self,height):
        '''return the material transection pk at this height
        0 represents no cra
        '''
        section_num=self.which_section(height)
        if section_num==0:
            return 0
        else:
            section=self.sections.get(section_num=section_num)
            return section.material_transection.pk
        
    def generate_material_transection_set(self):
        sections=self.sections.all()
        material_transection_set=set()
        for section in sections:
            material_transection=section.material_transection.pk
            material_transection_set.add(material_transection)
        return material_transection_set
    
    @property
    def material_set(self):
        material_transection_set=self.generate_material_transection_set()
        material_set=set()
        for material_transection in material_transection_set:
            material_set.update(MaterialTransection.objects.get(pk=material_transection).material_set)
        return material_set
    def __str__(self):
        if self.black:  
            return "{} black rod {}".format(self.reactor_model, self.active_length)
        else:
            return "{} grey rod {}".format(self.reactor_model, self.active_length)
        
class ControlRodSection(BaseModel):
    control_rod_type=models.ForeignKey(ControlRodType,related_name='sections')
    section_num=models.PositiveSmallIntegerField()
    length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material_transection=models.ForeignKey(MaterialTransection,related_name="control_rod_sections")
    
    class Meta:
        db_table='control_rod_section'
        ordering=['section_num']
        
        
    @property
    def previous_section(self):
        section_num=self.section_num
        if  section_num==1:
            return None
        else:
            return ControlRodSection.objects.get(control_rod_type=self.control_rod_type,section_num=section_num-1)
    
    @property
    def bottom_height(self):
        previous_section=self.previous_section
        if previous_section is None:
            bottom_height=Decimal('0')
        else:
            bottom_height =previous_section.length+ previous_section.bottom_height       
        return  bottom_height
    
    @property
    def pin_id(self):
        return self.material_transection.pin_id
    
    
    def __str__(self):
        return '{} {}'.format(self.control_rod_type,self.section_num)
    
    
class SourceRodType(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel)
    TYPE_CHOICES=(
                  ('primary','primary'),
                  ('secondary','secondary')
    )
    type=models.CharField(max_length=9,choices=TYPE_CHOICES)
    overall_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    material=models.ForeignKey(Material,blank=True,null=True)
    strength=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:10e8')
    
    class Meta:
        db_table='source_rod_type'
    
    def __str__(self):
        return '{} {}'.format(self.type, self.fuel_assembly_model)

class NozzlePlugRod(BaseModel):
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel)
    length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    class Meta:
        db_table='nozzle_plug_rod'
    
    def __str__(self):
        return '{} nozzle plug rod'.format(self.material)
    
    
class BurnablePoisonRod(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='bp_rod')
    active_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm') 
    bottom_height=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm based on the bottom of fuel active part') 
    diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',default=0.4838)                
    class Meta:
        db_table='burnable_poison_rod'
        #verbose_name='Burnable absorber rod'
        
    def get_active_volume(self,active_height):
        radius=self.diameter/2
        return Decimal(math.pi)*radius**2*active_height
    
    @property
    def height_lst(self):
        sections=self.sections.all()
        height_lst=[section.bottom_height for section in sections]
        #append the top part
        top_height=self.bottom_height+self.active_length
        fuel_active_height=self.fuel_assembly_model.active_length
        #bp is not long enough
        if top_height<fuel_active_height:
            height_lst.append(top_height)
        return height_lst
    
    @property
    def max_section_num(self):
        return self.sections.aggregate(Max('section_num'))['section_num__max']
    
    def which_section(self,height):
        '''
        based on the bottom of fuel active part
        0 represents no bp rod 
        '''
        #convert height to decimal
        if type(height)==Decimal:
            pass
        else:
            height=Decimal(str(height))
            
        height_lst=self.height_lst
        for i in range(len(height_lst)):
            if height_lst[i]>height:
                return i
            elif height_lst[i]==height:
                return i+1
            
        return len(height_lst) 
    
    def which_transection(self,height):
        '''return the material transection pk at this height
        0 represents no bpa
        '''
        section_num=self.which_section(height)
        if section_num==0 or section_num>self.max_section_num:
            return 0
        else:
            section=self.sections.get(section_num=section_num)
            return section.material_transection.pk
    def __str__(self):
        return '{} {} burnable poison rod'.format(self.pk,self.fuel_assembly_model)


class BurnablePoisonSection(BaseModel):
    burnable_poison_rod=models.ForeignKey(BurnablePoisonRod,related_name='sections')
    section_num=models.PositiveSmallIntegerField()
    length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material_transection=models.ForeignKey(MaterialTransection)
    class Meta:
        db_table='burnable_poison_section'
        ordering=['section_num']
        
    @property
    def previous_section(self):
        section_num=self.section_num
        if  section_num==1:
            return None
        else:
            return BurnablePoisonSection.objects.get(burnable_poison_rod=self.burnable_poison_rod,section_num=section_num-1)
    
    @property
    def bottom_height(self):
        previous_section=self.previous_section
        if previous_section is None:
            bottom_height=self.burnable_poison_rod.bottom_height
        else:
            bottom_height =previous_section.length+ previous_section.bottom_height       
        return  bottom_height
    
    @property
    def pin_id(self):
        return self.material_transection.pin_id
    
    def generate_base_pin_xml(self,guide_tube):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID=self.pin_id
        radial_map=self.material_transection.radial_materials.order_by('radius')
        radii_tup,mat_tup=zip(*[(str(item.radius),item.material.get_prerobin_identifier()) for item in radial_map])
  
        #insert into guide tube
        radii_lst=list(radii_tup)
        radii_lst.append(str(guide_tube.upper_inner_diameter))
        radii_lst.append(str(guide_tube.upper_outer_diameter))
        mat_lst=list(mat_tup)
        mat_lst.append('MOD')
        mat_lst.append(guide_tube.material.get_prerobin_identifier())
        
        radii=','.join(radii_lst)
        mat=','.join(mat_lst)
        
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        base_pin_xml.appendChild(ID_xml)
        
        radii_xml=doc.createElement('radii')
        radii_xml.appendChild(doc.createTextNode(radii))
        base_pin_xml.appendChild(radii_xml)
        
        mat_xml=doc.createElement('mat')
        mat_xml.appendChild(doc.createTextNode(mat))
        base_pin_xml.appendChild(mat_xml)
        
        return base_pin_xml
    
    def __str__(self):
        return '{} {}'.format(self.burnable_poison_rod,self.section_num)

######################################################################################################################
    
    

############################################################################
#the following three tables combine to describe burnable poison assembly   
class BurnablePoisonAssembly(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel)
    map=models.ManyToManyField(BurnablePoisonRod,through='BurnablePoisonAssemblyMap')
    symmetry=models.BooleanField(default=True,help_text="satisfy 1/8 symmetry")
    class Meta:
        db_table='burnable_poison_assembly'
        #verbose_name='Burnable absorber rod pattern'
        verbose_name_plural='burnable poison assemblies'
        order_with_respect_to="fuel_assembly_model"
    @property
    def height_lst(self):
        rods=self.map.all()
        height_set=set()
        for rod in rods:
            rod_set=set(rod.height_lst)
            height_set=height_set|rod_set
        height_lst=sorted(list(height_set))
        return height_lst
    
    @property
    def side_pin_num(self):
        return self.fuel_assembly_model.side_pin_num
    
    @property
    def bp_num(self):
        return self.get_poison_rod_num()
    
    @property
    def bottom_height(self):
        bottom_height=self.map.aggregate(Min('bottom_height'))['bottom_height__min']
        return bottom_height
    def generate_transection(self,height):
        side_num=self.side_pin_num
        rod_positions=self.rod_positions.all()
        transection={}
        if self.symmetry:
            for rod_position in rod_positions:
                if rod_position.in_triangle:
                    row=rod_position.row
                    column=rod_position.column
                    bpr=rod_position.burnable_poison_rod
                    rod_transection_pk=bpr.which_transection(height)
                    #has bpa at this height
                    if rod_transection_pk!=0:
                        transection[(row,column)]=rod_transection_pk
            
        else:
            for rod_position in rod_positions:
                position_4th=rod_position.reflect_4th_quandrant()
                if in_triangle(position_4th[0],position_4th[1],side_num):
                    bpr=rod_position.burnable_poison_rod
                    rod_transection_pk=bpr.which_transection(height)
                    #has bpa at this height
                    if rod_transection_pk!=0:
                        transection[position_4th]=rod_transection_pk
        
        return transection
    
    def get_poison_rod_num(self):
        num=self.rod_positions.count()
        return num  

    def get_quadrant_symbol(self):
        rod_map=self.rod_positions.all()
        symbol_lst=[]
        for rod in rod_map:
            pos=rod.position
            symbol=pos.generate_quadrant_symbol()
            if symbol not in symbol_lst:
                symbol_lst.append(symbol)
        
        return sorted(symbol_lst)
    
    def get_symmetry_bpa(self):
        if self.symmetry:
            return self
        else:
            num=self.get_poison_rod_num()
            quadrant_symbol_lst=self.get_quadrant_symbol()
            if quadrant_symbol_lst in [[1],[2],[3],[4]]:
                index=[1]
            elif quadrant_symbol_lst in [[1,2],[1,3],[3,4],[2,4]]:
                index=[1,2]
            elif quadrant_symbol_lst in [[1,2,3],[2,3,4],[1,2,4],[1,3,4]]:
                index=[1,2,3]
            
            for item in BurnablePoisonAssembly.objects.filter(fuel_assembly_model=self.fuel_assembly_model):
                if item.get_poison_rod_num()==num and item.get_quadrant_symbol()==index:
                    return item
            
    def generate_burnable_poison_assembly_xml(self):
        doc=minidom.Document()
        burnable_poison_assembly_xml=doc.createElement('burnable_poison_assembly')
        num=self.get_poison_rod_num()
        burnable_poison_assembly_xml.setAttribute('num', str(num))
        burnable_poison_assembly_xml.appendChild(doc.createTextNode(str(self.pk)))
        return burnable_poison_assembly_xml
    
    def __str__(self):
        num=self.rod_positions.count()
        return '{} {} {} {}'.format(self.pk,self.remark,num, self.fuel_assembly_model)

class BurnablePoisonAssemblyMap(BaseModel):
    burnable_poison_assembly=models.ForeignKey(BurnablePoisonAssembly,related_name='rod_positions')
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    burnable_poison_rod=models.ForeignKey(BurnablePoisonRod)
    
    class Meta:
        db_table='burnable_poison_assembly_map'
        
    @property
    def side_num(self):
        return self.burnable_poison_assembly.side_pin_num 
    @property    
    def position(self):
        return self.burnable_poison_assembly.fuel_assembly_model.positions.get(row=self.row,column=self.column)
    
    def get_position(self):
        side_num=self.side_num 
        row=self.row
        column=self.column 
        return (row,column,side_num)
    
    @property
    def in_triangle(self):
        '''to check if this position is in the 1/8 part to be calculated
        1|2
        ---
        3|4
        the lower triangle of quadrant 4
        '''
        position=self.get_position()
        return in_triangle(position[0], position[1], position[2])
    
    def generate_quadrant_symbol(self):
        position=self.get_position()
        return generate_quadrant_symbol(position[0], position[1], position[2])
    
    def reflect_4th_quandrant(self):
        position=self.get_position()
        return reflect_4th_quandrant(position[0], position[1], position[2])
    
    def __str__(self):
        return "{} R{}C{}".format(self.burnable_poison_assembly,self.row,self.column)
        
###############################################################################

class ControlRodAssemblyType(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel,related_name='cra_types')
    basez=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    side_pin_num=models.PositiveSmallIntegerField(default=17)
    map=models.ManyToManyField(ControlRodType,through='ControlRodAssemblyMap')
    symmetry=models.BooleanField(default=True,help_text="satisfy 1/8 symmetry")
    overall_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',default=400)
    class Meta:
        db_table='control_rod_assembly_type'
        order_with_respect_to = 'reactor_model'
        verbose_name='Control rod assembly'
        verbose_name_plural='Control rod assemblies'
    @property
    def cr_id(self):
        return "CR"+str(self.pk)
    @property
    def step_size(self):
        return self.reactor_model.control_rod_step_size
    
    @property
    def start_index(self):
        order=self.reactor_model.get_controlrodassemblytype_order()
        self_order=order.index(self.pk)
        #first one
        if self_order==0:
            return 1
        else:
            return self.get_previous_in_order().end_index+1
        
    @property
    def end_index(self):
        return self.start_index+self.layers_num-1
    
    @property
    def layers_num(self):
        return len(self.height_lst)
    
    def generate_base_control_rod_xml(self):
        spider=0
        doc=minidom.Document()
        base_control_rod_xml=doc.createElement("base_control_rod")
        base_control_rod_xml.setAttribute("cr_id", self.cr_id)
        base_control_rod_xml.setAttribute("spider", str(spider))
        
        axial_length_xml=doc.createElement("axial_length")
        length_lst=map(str,self.length_lst)
        axial_length_xml.appendChild(doc.createTextNode(" ".join(length_lst)))
        base_control_rod_xml.appendChild(axial_length_xml)
        
        axial_type_xml=doc.createElement("axial_type")
        type_lst=map(str,self.type_lst)
        axial_type_xml.appendChild(doc.createTextNode(" ".join(type_lst)))
        base_control_rod_xml.appendChild(axial_type_xml)
        return base_control_rod_xml
    
    def black_grey_rod_num(self):
        control_rods=self.map.all()
        bnum=0
        gnum=0
        for control_rod in control_rods:
            if control_rod.black:
                bnum+=1
            else:
                gnum+=1
        return (bnum,gnum)
    @property
    def grey(self):
        if self.black_grey_rod_num()[1]!=0:
            return True
        return False
    
    @property
    def length_lst(self):
        overall_length=self.overall_length
        height_lst=self.height_lst
        height_lst.append(overall_length)
        
        length_lst=[height_lst[i+1]-height_lst[i] for i in range(len(height_lst)-1)]
        return length_lst
    
    @property    
    def type_lst(self):
        return list(range(self.start_index,self.end_index+1))
            
    @property
    def height_lst(self):
        rods=self.map.all()
        height_set=set()
        for rod in rods:
            rod_set=set(rod.height_lst)
            height_set=height_set|rod_set
        height_lst=sorted(list(height_set))
        
        result_lst=[]
        if len(height_lst)==1:
            result_lst=height_lst
        else:
            transection_lst=[]
            for height in height_lst:
                transection=self.generate_transection(height)
                if transection not in transection_lst:
                    result_lst.append(height)
                    transection_lst.append(transection)
        
        return sorted(result_lst)
    
    def generate_transection(self,height):
        if self.symmetry:
            rod_positions=self.rod_positions.all()
            transection={}
            for rod_position in rod_positions:
                if rod_position.in_triangle:
                    row=rod_position.row
                    column=rod_position.column
                    crt=rod_position.control_rod_type
                    rod_transection_pk=crt.which_transection(height)
                    #has crt at this height
                    if rod_transection_pk!=0:
                        transection[(row,column)]=rod_transection_pk
            return transection
        else:
            return None
    
    
    def get_branch_ID(self,height):
        return "CRD_{}_{}".format(self.pk,height)
    
    def get_branch_ID_set(self):
        lst= [self.get_branch_ID(height) for height in self.height_lst]
        return set(lst)
    
    def generate_base_branch_xml(self,height):
        transection=self.generate_transection(height)
        doc=minidom.Document()
        base_branch_xml=doc.createElement('base_branch')
        branch_ID=self.get_branch_ID(height)
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(branch_ID))
        base_branch_xml.appendChild(ID_xml)
        
        side_num=self.side_pin_num
        half=int(side_num/2)+1
        #CRD
        CRD='\n'
        for row in range(half,side_num+1):
            row_lst=[]
            for col in range(half,row+1):
                pos=(row,col)
                if pos in transection:
                    pk=transection[pos]
                    mt=MaterialTransection.objects.get(pk=pk)
                    row_lst.append(mt.pin_id)
                else:
                    row_lst.append('NONE')
            
            CRD +=('  '.join(row_lst)+'\n')
        
        CRD_xml=doc.createElement('CRD')
        CRD_xml.appendChild(doc.createTextNode(CRD))
        base_branch_xml.appendChild(CRD_xml)
        
        return base_branch_xml
    
    def generate_base_branch_xml_lst(self):
        base_branch_xml_lst=[]
        for height in self.height_lst:
            base_branch_xml=self.generate_base_branch_xml(height)
            base_branch_xml_lst.append(base_branch_xml)
            
        return base_branch_xml_lst
        
    def __str__(self):
        descrip="grey rod" if self.grey else "black rod"
        return '{} {}'.format(self.reactor_model,descrip)

class ControlRodAssemblyMap(BaseModel):
    control_rod_assembly_type=models.ForeignKey(ControlRodAssemblyType,related_name='rod_positions')
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    control_rod_type=models.ForeignKey(ControlRodType)
    
    
    class Meta:
        db_table='control_rod_assembly_map'
    def clean(self):
        side_pin_num=self.control_rod_assembly_type.side_pin_num
        if self.row>side_pin_num:
            raise ValidationError({'row':_('the row or column is bigger than side pin number'),                         
            })
        if self.column>side_pin_num:
            raise ValidationError({'column':_('the column is bigger than side pin number'),                     
            })
            
    @property
    def in_triangle(self):
        '''to check if this position is in the 1/8 part to be calculated
        1|2
        ---
        3|4
        the lower triangle of quadrant 4
        '''
        side_num=self.control_rod_assembly_type.side_pin_num 
        row=self.row
        column=self.column
        return in_triangle(row, column, side_num)
        

        
    def __str__(self):
        return '{} {}'.format(self.control_rod_assembly_type,self.control_rod_type)
  
    
class ControlRodCluster(BaseModel):
    control_rod_assembly_type=models.ForeignKey(ControlRodAssemblyType,related_name='clusters')
    cluster_name=models.CharField(max_length=5)
    class Meta:
        db_table='control_rod_cluster'
        
    def get_control_rod_assembly_num(self):
        return self.control_rod_assemblies.count()
    get_control_rod_assembly_num.short_description='same cluster number'
    
    @property
    def reactor_model(self):
        return self.control_rod_assembly_type.reactor_model
    
    @property
    def step_size(self):
        return self.control_rod_assembly_type.step_size
    @property
    def basez(self):
        return self.control_rod_assembly_type.basez
    
    def __str__(self):
        return '{} {}'.format(self.pk,self.cluster_name)
    
# #the following two models describe control rod assembly
# class ControlRodAssembly(BaseModel):
#     cluster=models.ForeignKey(ControlRodCluster,related_name='control_rod_assemblies',blank=True,null=True)
#     
#     class Meta:
#         db_table='control_rod_assembly'
#         verbose_name_plural='Control rod assemblies'
#         
#     @property
#     def cluster_name(self):
#         return self.cluster.cluster_name
#     @property
#     def reactor_model(self):
#         return self.cluster.reactor_model
#     @property
#     def step_size(self):
#         return self.cluster.step_size
#     @property
#     def basez(self):
#         return self.cluster.basez
#         
#     def __str__(self):
#         return '{} {}'.format(self.pk,self.cluster)


##############################################################################
#the following four models combine to describe source assembly 
class SourceAssembly(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel)
    source_rod_map=models.ManyToManyField(FuelAssemblyPosition,through='SourceRodMap')
    
    class Meta:
        db_table='source_assembly' 
        verbose_name_plural='Source assemblies'   
        
    def __str__(self):
        obj=SourceAssembly.objects.get(pk=self.pk)
        num=obj.source_rod_positions.filter(source_rod__type='primary').count()    
        if num:
            name='primary'
        else:
            name='secondary'
       
        return '{} {} source assembly'.format(self.fuel_assembly_model,name)
    
class SourceRodMap(BaseModel):
    source_assembly=models.ForeignKey(SourceAssembly,related_name='source_rod_positions')
    source_rod_position=models.ForeignKey(FuelAssemblyPosition,limit_choices_to={'type': 'guide'})
    source_rod=models.ForeignKey(SourceRodType)
    
    class Meta:
        db_table='source_rod_map'
    
    def __str__(self):
        return '{} {}'.format(self.source_assembly, self.source_rod_position)


class SourceAssemblyLoadingPattern(BaseModel):
    cycle=models.ForeignKey(Cycle,related_name='source_assembly_positions')
    reactor_position=models.ForeignKey(ReactorPosition)
    source_assembly=models.ForeignKey(SourceAssembly)
    
    

    class Meta:
        db_table='source_assembly_loading_pattern'
        unique_together=('cycle','reactor_position')
        
    
    def __str__(self):
        return '{} {}'.format(self.cycle, self.reactor_position)  
    
    
    
    
################################################################################ 
#the following 2 models describe nozzle plug assembly

class NozzlePlugAssembly(BaseModel):
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:Kg')
    nozzle_plug_rod=models.ManyToManyField(NozzlePlugRod,through='NozzlePlugRodMap')
    
    class Meta:
        db_table='nozzle_plug_assembly'
        verbose_name_plural='Nozzle plug assemblies'
    
    def __str__(self):
        return '{}'.format(self.weight) 

class NozzlePlugRodMap(BaseModel):
    nozzle_plug_assembly=models.ForeignKey(NozzlePlugAssembly)
    guid_tube_position=models.OneToOneField(FuelAssemblyPosition,limit_choices_to={'type': 'guide'})
    nozzle_plug_rod=models.ForeignKey(NozzlePlugRod)
    
    class Meta:
        db_table='nozzle_plug_rod_map'
        
    def __str__(self):
        return '{} {}'.format(self.nozzle_plug_assembly, self.nozzle_plug_rod)
    

class OperationDailyParameter(BaseModel):
    cycle=models.ForeignKey(Cycle)
    date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True) 
    burnup=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:MWd/tU',blank=True,null=True)
    delta_time=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:day',blank=True,null=True)
    relative_power=models.DecimalField(max_digits=10, decimal_places=9,validators=[MinValueValidator(0),MaxValueValidator(1)],)
    critical_boron_density=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:ppm')
    axial_power_offset=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    control_rod_step=models.ManyToManyField(ControlRodCluster,through='ControlRodAssemblyStep')
    
    class Meta:
        db_table='operation_daily_parameter'
        order_with_respect_to = 'cycle'
        verbose_name='Daily operation history'
        verbose_name_plural='Daily operation history'
    def generate_depl_case_node(self):
        doc = minidom.Document()
        depl_case_xml=doc.createElement('depl_case')
        core_state_xml=doc.createElement('core_state')
        depl_case_xml.appendChild(core_state_xml)
        #handle relative power
        relative_power_xml=doc.createElement('relative_power')
        relative_power_xml.appendChild(doc.createTextNode(str(self.relative_power)))
        core_state_xml.appendChild(relative_power_xml)
        #handle burnup or delta time
        burnup=self.burnup
        if burnup is not None:
            burnup_xml=doc.createElement('burnup')
            burnup_xml.appendChild(doc.createTextNode(str(self.burnup)))
            core_state_xml.appendChild(burnup_xml)
        else:
            delta_time_xml=doc.createElement('delta_time')
            delta_time_xml.appendChild(doc.createTextNode(str(self.delta_time)))
            core_state_xml.appendChild(delta_time_xml)
        #handle control rod
        for item in self.control_rods.all():
            rcca_xml=doc.createElement('rcca')
            rcca_xml.appendChild(doc.createTextNode(str(item.step)))
            rcca_xml.setAttribute('id', item.control_rod_cluster.cluster_name)
            core_state_xml.appendChild(rcca_xml)
        return depl_case_xml
       
    def __str__(self):
        return '{}'.format(self.date)  
    
class ControlRodAssemblyStep(BaseModel):
    operation=models.ForeignKey(OperationDailyParameter,related_name='control_rods')
    control_rod_cluster=models.ForeignKey(ControlRodCluster)
    step=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)])
    
    class Meta:
        db_table='control_rod_assembly_step'
    
    @property
    def cluster_name(self):
        return self.control_rod_cluster.cluster_name
        
    def __str__(self):
        return '{} {}'.format(self.control_rod_cluster, self.step)


def get_monthly_data_upload_path(instance,filename):
    cycle=instance.cycle
    unit=cycle.unit
    plant=unit.plant
    plant_name=plant.abbrEN
    name=os.path.basename(filename)
    return 'operation_data/{}/unit{}/cycle{}/{}'.format(plant_name,unit.unit, cycle.cycle,name) 

class OperationMonthlyParameter(BaseModel):  
    cycle=models.ForeignKey(Cycle)
    date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True)
    avg_burnup=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:MWd/tU',blank=True,null=True)
    relative_power=models.DecimalField(max_digits=10, decimal_places=9,validators=[MinValueValidator(0),MaxValueValidator(1)],blank=True,null=True)
    boron_concentration=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:ppm',blank=True,null=True)
    axial_power_offset=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    #FDH=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:')
    FQ=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:',blank=True,null=True)
    raw_file=models.FileField(upload_to=get_monthly_data_upload_path,)
    bank_position=models.ManyToManyField(ControlRodCluster,through='OperationBankPosition')
    distribution=models.ManyToManyField(ReactorPosition,through='OperationDistributionData')
    
    class Meta:
        db_table='operation_monthly_parameter'
        order_with_respect_to = 'cycle'
        verbose_name='Incore flux mapping result'    
    def __str__(self):
        return "{}".format(self.cycle,)
    
class OperationBankPosition(BaseModel):
    operation=models.ForeignKey(OperationMonthlyParameter,related_name='cluster_steps')
    control_rod_cluster=models.ForeignKey(ControlRodCluster)
    step=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)])
    
    class Meta:
        db_table='operation_bank_position'
        order_with_respect_to = 'operation'
    @property
    def cluster_name(self):
        return self.control_rod_cluster.cluster_name
      
    def __str__(self):
        return "{}".format(self.operation,)
    
    
    
class OperationDistributionData(BaseModel):
    operation=models.ForeignKey(OperationMonthlyParameter,related_name='distribution_data')
    reactor_position=models.ForeignKey(ReactorPosition)
    relative_power=models.DecimalField(max_digits=10, decimal_places=9,validators=[MinValueValidator(0),MaxValueValidator(1)],)
    FDH=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:')
    axial_power_offset=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    
    class Meta:
        db_table='operation_distribution_data'
        order_with_respect_to = 'operation'
        verbose_name_plural='operation_distribution_data'
    def position(self):
        reactor_position=self.reactor_position
        return "{}_{}".format(reactor_position.row,reactor_position.column)
        
    def __str__(self):
        return "{}".format(self.operation,)
    
    
