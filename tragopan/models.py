from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Max, Sum
#token generated automatically when creating a new user
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import os
import tempfile
from xml.dom import minidom
from decimal import Decimal
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

#some common constant
MEDIA_ROOT=settings.MEDIA_ROOT
BASIC_DATA_PATH=os.path.join(MEDIA_ROOT,'basic_data')    
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
    id_wims=models.PositiveIntegerField(unique=True)
    id_self_defined=models.PositiveIntegerField(unique=True,blank=True,null=True)
    amu= models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),])
    nf=models.PositiveSmallIntegerField(choices=NF_CHOICES)
    material_type= models.CharField(max_length=4,choices=MATERIAL_TYPE_CHOICES)
    descrip= models.CharField(max_length=50)
   
    @staticmethod
    def autocomplete_search_fields():
        return ("element__symbol",'id_wims')
    
    @property
    def res_trig(self):
        return 0 if self.nf in (0,4) else 1

    
    @property
    def dep_trig(self):
        return 1 if self.material_type in ('FP','A','B','B/FP') else 0
 
    
    @classmethod
    def generate_nuclide_lib(cls):
        data=cls.objects.all()
        for item in data:
            yield (item.pk,item.id_wims,item.amu,item.res_trig,item.dep_trig)
    
    class Meta:
        db_table='wims_nuclide_data'
        
            
    def __str__(self):
        return "{}".format(self.nuclide_name)
  
class WmisElementData(BaseModel):
    element_name=models.CharField(max_length=30,)
    composition=models.ManyToManyField(WimsNuclideData,through='WmisElementComposition')
    
    @staticmethod
    def autocomplete_search_fields():
        return ("element_name__icontains",)
    def get_nuclide_num(self):  
        return self.composition.count()
    
    class Meta:
        db_table='wmis_element_data'
        
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
                           (2,'mixture'),
                           (3,'symbolic'),
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
    
    #class attribute
    material_element_lib_path=os.path.join(BASIC_DATA_PATH,'material_element.lib')
    
    @classmethod
    def generate_material_lib(cls):
        if not os.path.exists(BASIC_DATA_PATH):
            os.makedirs(BASIC_DATA_PATH)
        f=open(cls.material_element_lib_path,'w')
        
        #write general info
        general_descrip=['nuclides','elements','compounds','mixtures']
        f.write(format_line(general_descrip))
        
        nuclide_num=WimsNuclideData.objects.count()
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
            for compo in element.nuclides.all():
                nuclide_info=[' ',compo.wmis_nuclide.pk,compo.weight_percent/100] 
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
    INPUT_METHOD_CHOICES=(
                          (1,'fuel by enrichment'),
                          (2,'blend materials with B10 linear density'),
                          (3,'blend materials '),
                          (4,'totally inherit from basic material'),
                          (5,'inherit from basic material with B10 linear density'),
    )
    nameCH=models.CharField(max_length=40,blank=True)
    nameEN=models.CharField(max_length=40,blank=True)
    mixture_composition=models.ManyToManyField('self',symmetrical=False,through='MixtureComposition',through_fields=('mixture','material',))
    bpr_B10=models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),],help_text=r"mg/cm",blank=True,null=True)
    enrichment=models.DecimalField(max_digits=9, decimal_places=6,validators=[MinValueValidator(0),],help_text=r"U235:%",blank=True,null=True)
    input_method=models.PositiveSmallIntegerField(choices=INPUT_METHOD_CHOICES,default=1)
    basic_material=models.OneToOneField(BasicMaterial,blank=True,null=True)
    
    class Meta:
     
        db_table='material'
        verbose_name='Material repository'
        verbose_name_plural='Material repository'
        
    def clean(self):
        if self.input_method==1:
            if not self.enrichment:
                raise ValidationError({'enrichment':_('enrichment cannot be blank when you choose such input method'),                           
            }) 
            if not self.nameEN:
                raise ValidationError({'nameEN':_('nameEN cannot be blank when you choose such input method'),                           
            }) 
        elif self.input_method==2:
            if not self.bpr_B10:
                raise ValidationError({'bpr_B10':_('bpr_B10 cannot be blank when you choose such input method'),                           
            }) 
            if not self.nameEN:
                raise ValidationError({'nameEN':_('nameEN cannot be blank when you choose such input method'),                           
            }) 
        elif self.input_method==3:
            if not self.nameEN:
                raise ValidationError({'nameEN':_('nameEN cannot be blank when you choose such input method'),                           
            }) 
                
        elif self.input_method==4:
            if not self.basic_material:
                raise ValidationError({'basic_material':_('basic_material cannot be blank when you choose such input method'),                           
            }) 
        elif self.input_method==5:
            if not self.bpr_B10:
                raise ValidationError({'bpr_B10':_('bpr_B10 cannot be blank when you choose such input method'),                           
            }) 
            if not self.basic_material:
                raise ValidationError({'basic_material':_('basic_material cannot be blank when you choose such input method'),                           
            })  
            
    @property
    def prerobin_identifier(self):
        if self.input_method==4:
            return self.basic_material.name
        elif self.input_method==1:
            return 'FUEL_'+str(self.pk)
        elif self.input_method==5:
            return self.basic_material.name
        #grid homgenized with moderator
        elif self.input_method==3:
            return 'HOMG_'+str(self.pk)
        else:
            return self.nameEN
    
    def generate_base_mat(self):
        result={'ID':self.prerobin_identifier}
        if self.input_method==1:
            result['density']=self.attribute.density
            result['composition_ID']='UO2_'+str(self.enrichment)
        elif self.input_method==2:
            result['bpr_B10']=self.bpr_B10
            compo=self.mixtures.all()
            composition_ID_lst=[item.material.prerobin_identifier for item in compo]
            weight_percent_lst=[str(item.percent) for item in compo]
            result['composition_ID']=','.join(composition_ID_lst)
            result['weight_percent']=','.join(weight_percent_lst)
        elif self.input_method==3:
            compo=self.mixtures.all()
            homgenized_mat_lst=[item.material.prerobin_identifier for item in compo]
            result['homgenized_mat']=','.join(homgenized_mat_lst)
            input_method=compo.first().input_method
            percent_lst=[str(item.percent) for item in compo]
            #by weight
            if input_method==1:
                result['weight_percent']=','.join(percent_lst)
            else:
                result['volume_percent']=','.join(percent_lst)
                
        elif self.input_method==4:
            return {}
        elif self.input_method==5:
            result['bpr_B10']=self.bpr_B10
            result['composition_ID']=self.basic_material.name
            
        return  result  
    
    #class attribute
    material_databank_path=os.path.join(PRE_ROBIN_PATH,'material_databank.xml')
    @classmethod
    def generate_material_databank_xml(cls):
        if not os.path.exists(PRE_ROBIN_PATH):
            os.makedirs(PRE_ROBIN_PATH)
        f=open(cls.material_databank_path,'w')
        
        doc = minidom.Document()
        material_databank_xml=doc.createElement('material_databank')
        materials=cls.objects.all()
        for material in  materials:
            base_mat=material.generate_base_mat()
            if base_mat:
                base_mat_xml=doc.createElement('base_mat')
                for key,value in base_mat.items():
                    key_xml=doc.createElement(str(key))
                    key_xml.appendChild(doc.createTextNode(str(value)))
                    base_mat_xml.appendChild(key_xml)
                material_databank_xml.appendChild(base_mat_xml)
                
        doc.appendChild(material_databank_xml)          
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        f.close()
                    
        
            
    def __str__(self):
        return self.prerobin_identifier
    
class MixtureComposition(BaseModel):
    INPUT_METHOD_CHOICES=(
                          (1,'by weight'),
                          (2,'by volume'),
                        
    )
    mixture=models.ForeignKey(Material,related_name='mixtures',)
    material=models.ForeignKey(Material)
    percent=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    input_method=models.PositiveSmallIntegerField(choices=INPUT_METHOD_CHOICES,default=1)
    class Meta:
        db_table='mixture_composition'
    
             
    def __str__(self):
        return "{} {}".format(self.mixture, self.material)
                
      
class MaterialAttribute(BaseModel):
    material=models.OneToOneField(Material,related_name='attribute')
    density=models.DecimalField(max_digits=15, decimal_places=5,help_text=r'unit:g/cm3')
    heat_capacity=models.DecimalField(max_digits=15, decimal_places=5,help_text=r'J/kg*K',blank=True,null=True)
    thermal_conductivity=models.DecimalField(max_digits=15, decimal_places=5,help_text=r'W/m*K',blank=True,null=True)
    expansion_coefficient=models.DecimalField(max_digits=15, decimal_places=5,help_text=r'm/K',blank=True,null=True)
    code = models.CharField(max_length=10, blank=True)
    class Meta:
        db_table='material_attribute'
        
    def __str__(self):
        return str(self.material)+"'s attribute"
    

    
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
    
    class Meta:
        db_table='plant'
        
    @property
    def plant_dir(self):
        media_root=settings.MEDIA_ROOT
        plant_dir=os.path.join(media_root, self.abbrEN)
        return plant_dir
    
    @property    
    def ibis_dir(self):
        plant_dir=self.plant_dir
        ibis_dir=os.path.join(plant_dir,'ibis_files')
        return ibis_dir
    
    def __str__(self):
        return self.abbrEN  
    
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


    name = models.CharField(max_length=50,choices=MODEL_CHOICES)
    generation = models.CharField(max_length=2, choices=GENERATION_CHOICES)
    reactor_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    geometry_type = models.CharField(max_length=9, choices=GEOMETRY_CHOICES)
    row_symbol = models.CharField(max_length=6, choices=SYMBOL_CHOICES)
    column_symbol = models.CharField(max_length=6, choices=SYMBOL_CHOICES)
    num_loops = models.PositiveSmallIntegerField(blank=True,null=True)
    fuel_pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    core_equivalent_diameter = models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    active_height= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    cold_state_assembly_pitch= models.DecimalField(max_digits=7, decimal_places=4,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    hot_state_assembly_pitch = models.DecimalField(max_digits=7, decimal_places=4,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    vendor = models.ForeignKey(Vendor)  
    thermal_couple_position=models.ManyToManyField('ReactorPosition',related_name='thermal_couple_position',db_table='thermal_couple_map',blank=True,)
    incore_instrument_position=models.ManyToManyField('ReactorPosition',related_name='incore_instrument_position',db_table='incore_instrument_map',blank=True,)
   
    class Meta:
        db_table = 'reactor_model'
        
    def get_max_row_column(self):
        positions=self.positions.all()
        max_row=positions.aggregate(Max('row'))['row__max']
        max_column=positions.aggregate(Max('column'))['column__max']
        return [max_row,max_column]
    

    
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
        
   
        
        
    def get_quadrant_symbol(self):
        '''
        2|1
        ---
        3|4
        '''
        [max_row,max_column]=self.reactor_model.get_max_row_column()
        
        if self.row<max_row/2 and self.column<max_column/2+1:
            return 2
        elif self.row<max_row/2+1 and self.column>max_column/2:
            return 1
        elif self.row>max_row/2 and self.column<max_column/2:
            
            return 3
        else:
            return 4
        
    
        
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
    
class CoreBaffle(BaseModel):
    reactor_model=models.OneToOneField(ReactorModel)
    gap_to_fuel=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    outer_diameter=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    material = models.ForeignKey(Material)
    thickness= models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    weight=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:Kg',blank=True,null=True)
    vendor = models.ForeignKey(Vendor)
    class Meta:
        db_table='core_baffle'
    
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
    reactor_model = models.ForeignKey(ReactorModel)
    electric_power = models.DecimalField(max_digits=10, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:MW')
    thermal_power = models.DecimalField(max_digits=10, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:MW')
    heat_fraction_in_fuel = models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%")
    primary_system_pressure= models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:MPa')
    ave_linear_power_density= models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:KW/m')
    ave_vol_power_density = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:KW/L', blank=True, null=True)
    ave_mass_power_density = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:W/g (fuel)')
    best_estimated_cool_vol_flow_rate = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:m3/h', blank=True, null=True)
    best_estimated_cool_mass_flow_rate = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:kg/h', blank=True, null=True)
    coolant_volume=models.DecimalField(max_digits=20, decimal_places=5,validators=[MinValueValidator(0)],help_text=r'unit:m3', blank=True, null=True)
    bypass_flow_fraction = models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%", blank=True, null=True)
    cold_state_cool_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K')
    HZP_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K')
    HFP_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K')
    HFP_core_ave_cool_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    mid_power_cool_inlet_temp = models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:K', blank=True, null=True)
    boron_density=models.PositiveSmallIntegerField(default=500,help_text='ppm')
    fuel_temperature=models.PositiveSmallIntegerField(default=903,help_text='K')
    moderator_temperature=models.PositiveSmallIntegerField(default=577,help_text='K')
    class Meta:
        db_table = 'unit_parameter'
        unique_together = ('plant', 'unit')
    
    @property
    def unit_dir(self):
        plant=self.plant
        return os.path.join(plant.plant_dir,'unit'+str(self.unit))
    
    @property     
    def depletion_state_lst(self):
        primary_system_pressure=self.primary_system_pressure
        ave_mass_power_density=self.ave_mass_power_density
        boron_density=self.boron_density
        fuel_temperature=self.fuel_temperature
        moderator_temperature=self.moderator_temperature
        return [primary_system_pressure,fuel_temperature,moderator_temperature,boron_density,ave_mass_power_density]
    @property    
    def base_component_path(self):
        plant=self.plant
        base_component_path=os.path.join(plant.plant_dir,'base_component.xml')
        if os.path.isfile(base_component_path):
            return base_component_path
    
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
            if result_cycle.fuel_assembly_loading_patterns.all():
                return result_cycle
            result_cycle=result_cycle.get_pre_cycle()
    get_current_cycle.short_description='current cycle'   
    
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
    
    def duplicate_cra_lp(self,base_cycle):
        
        base_cra_lps=base_cycle.control_rod_assembly_loading_patterns.all()
        for base_cra_lp in base_cra_lps:
            reactor_position=base_cra_lp.reactor_position
            control_rod_assembly=base_cra_lp.control_rod_assembly
            control_rod_assembly.pk=None
            control_rod_assembly.save()
            ControlRodAssemblyLoadingPattern.objects.create(reactor_position=reactor_position,cycle=self,control_rod_assembly=control_rod_assembly)
        
            
        
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
            falp=self.fuel_assembly_loading_patterns.get(reactor_position=reactor_position)
            return falp
        except:
            return None
        
    def get_cra_cycle(self):
        
        this_cycle=self
        while this_cycle:
            cra=this_cycle.control_rod_assembly_loading_patterns.all()
            
            if cra:
                return this_cycle
            this_cycle=this_cycle.get_pre_cycle()
            
            
    def generate_fuel_node(self):  
        doc = minidom.Document()      
        fuel_xml=doc.createElement('fuel')
        doc.appendChild(fuel_xml)
        fuel_xml=doc.createElement('fuel')
        fuel_assembly_loading_patterns=self.fuel_assembly_loading_patterns.all()
        
        for item in fuel_assembly_loading_patterns:
            #position info
            fuel_position_xml=doc.createElement('position')
            fuel_xml.appendChild(fuel_position_xml)
            reactor_position=item.reactor_position
            row=reactor_position.row
            column=reactor_position.column
            fuel_position_xml.setAttribute('row', str(row))
            fuel_position_xml.setAttribute('column', str(column))
            
            #assembly info
            fuel_assembly_xml=doc.createElement('fuel_assembly')
            fuel_position_xml.appendChild(fuel_assembly_xml)
            fuel_assembly=item.fuel_assembly
            pk=fuel_assembly.pk
            type=fuel_assembly.type
            enrichment=type.assembly_enrichment
            assembly_name=type.assembly_name
            
            fuel_assembly_xml.appendChild(doc.createTextNode(str(type.pk)))
            fuel_assembly_xml.setAttribute('id', str(pk))
            fuel_assembly_xml.setAttribute('enrichment', str(enrichment))
            fuel_assembly_xml.setAttribute('assembly_name', str(assembly_name))
            #previous cycle info
            previous=item.get_previous()
            if previous:
                previous_xml=doc.createElement('previous')
                fuel_position_xml.appendChild(previous_xml)
                data=previous.split(sep='-') 
                previous_xml.setAttribute('row', data[1])
                previous_xml.setAttribute('column', data[2])
                previous_xml.appendChild(doc.createTextNode(data[0]))
                
            first=fuel_assembly.get_first_loading_pattern()
            first_cycle=first.cycle
            first_position=first.reactor_position
            first_xml=doc.createElement('first')
            fuel_position_xml.appendChild(first_xml)
            first_xml.setAttribute('row', str(first_position.row))
            first_xml.setAttribute('column', str(first_position.column))
            first_xml.appendChild(doc.createTextNode(str(first_cycle.cycle)))
            
        return fuel_xml    
    
    def generate_bpa_node(self):
        doc = minidom.Document()
        bpa_xml=doc.createElement('bpa')
        bpa_loading_patterns=self.bpa_loading_patterns.all()
        for item in bpa_loading_patterns:
            #position info
            bpa_position_xml=doc.createElement('position')
            bpa_xml.appendChild(bpa_position_xml)
            reactor_position=item.reactor_position
            row=reactor_position.row
            column=reactor_position.column
            bpa_position_xml.setAttribute('row', str(row))
            bpa_position_xml.setAttribute('column', str(column))
            
            #bpa info
            burnable_poison_assembly=item.burnable_poison_assembly
            burnable_poison_assembly_xml=doc.createElement('burnable_poison_assembly')
            bpa_position_xml.appendChild(burnable_poison_assembly_xml)
            rod_num=burnable_poison_assembly.get_poison_rod_num()
            #rod_height=burnable_poison_assembly.get_poison_rod_height()
            burnable_poison_assembly_xml.setAttribute('id', str(burnable_poison_assembly.pk))
            #burnable_poison_assembly_xml.setAttribute('height', str(rod_height))
            burnable_poison_assembly_xml.appendChild(doc.createTextNode(str(rod_num)))
        return bpa_xml
    
    def generate_cra_node(self):
        doc = minidom.Document()  
        cra_xml=doc.createElement('cra')
        cra_loading_patterns=self.control_rod_assembly_loading_patterns.all()
        for item in cra_loading_patterns:
            #position info
            cra_position_xml=doc.createElement('position')
            cra_xml.appendChild(cra_position_xml)
            reactor_position=item.reactor_position
            row=reactor_position.row
            column=reactor_position.column
            cra_position_xml.setAttribute('row', str(row))
            cra_position_xml.setAttribute('column', str(column))
            
            #cra info
            control_rod_assembly=item.control_rod_assembly
            control_rod_assembly_xml=doc.createElement('control_rod_assembly')
            cra_position_xml.appendChild(control_rod_assembly_xml)
            
            cluster_name=control_rod_assembly.cluster_name
            type=control_rod_assembly.type
            step_size=control_rod_assembly.step_size
            basez=control_rod_assembly.basez
            control_rod_assembly_xml.setAttribute('id', str(control_rod_assembly.pk))
            control_rod_assembly_xml.setAttribute('type', str(type))
            control_rod_assembly_xml.setAttribute('step_size', str(step_size))
            control_rod_assembly_xml.setAttribute('basez', str(basez))
            control_rod_assembly_xml.appendChild(doc.createTextNode(cluster_name)) 
        return  cra_xml
    
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
        #generate child nodes respectively
        fuel_node=self.generate_fuel_node()
        bpa_node=self.generate_bpa_node()
        cra_node=self.generate_cra_node() 
        
        loading_pattern_xml.appendChild(fuel_node)
        if bpa_node is not None:
            loading_pattern_xml.appendChild(bpa_node)
        if cra_node is not None:
            loading_pattern_xml.appendChild(cra_node)
            
        f = tempfile.TemporaryFile(mode='w+')
        #f=open('/home/django/Desktop/mylp.xml','w')
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        
        return f
            
            
        
    def __str__(self):
        return '{}C{}'.format(self.unit, self.cycle)
    
class FuelAssemblyLoadingPattern(BaseModel):
    ROTATION_DEGREE_CHOICES=(
        ('0','0'),
        ('90','90'),
        ('180','180'),
        ('270','270'),
    )
    cycle=models.ForeignKey(Cycle,related_name='fuel_assembly_loading_patterns')
    reactor_position=models.ForeignKey(ReactorPosition)
    fuel_assembly=models.ForeignKey('FuelAssemblyRepository',related_name='cycle_positions',default=1)
    rotation_degree=models.CharField(max_length=3,choices=ROTATION_DEGREE_CHOICES,default='0',help_text='anticlokwise')
    
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
            previous_cycles=[]
            for item in falp:
                previous_cycles.append(item.cycle.cycle)
                
              
            last_cycle=max(previous_cycles)   
            last_position=falp.get(cycle__cycle=last_cycle).reactor_position
            return "{}-{}-{}".format(last_cycle,last_position.row,last_position.column)
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
        cycle=self.cycle
        reactor_position=self.reactor_position
        try:
            BurnablePoisonAssemblyLoadingPattern.objects.get(cycle=cycle,reactor_position=reactor_position)
            return True
        except:
            return False
    
    def if_insert_cra(self):
        cycle=self.cycle
        reactor_position=self.reactor_position
        
        try:
            cra_cycle=cycle.get_cra_cycle()
            ControlRodAssemblyLoadingPattern.objects.get(cycle=cra_cycle,reactor_position=reactor_position)
            return True
        except:
            return False
            
        
    def get_grid(self):
        fuel_assembly=self.fuel_assembly
        grids=fuel_assembly.type.model.grid_pos.all()
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
    name=models.CharField(max_length=20)
    overall_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    side_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    assembly_pitch=models.DecimalField(max_digits=7, decimal_places=4,validators=[MinValueValidator(0)],help_text='unit:cm')
    pin_pitch=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    lower_gap=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    upper_gap=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
    side_pin_num=models.PositiveSmallIntegerField(default=17)
    licensed_max_discharge_BU =models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='MWd/tU',blank=True,null=True)
    licensed_pin_discharge_BU =models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='MWd/tU',blank=True,null=True)
    vendor=models.ForeignKey(Vendor)
    
    class Meta:
        db_table='fuel_assembly_model'
        
    def generate_assembly_model_xml(self,symmetry=8):
        doc = minidom.Document()
        assembly_model_xml=doc.createElement('assembly_model')
        model_ID_xml=doc.createElement('model_ID')
        model_ID_xml.appendChild(doc.createTextNode(self.name))
        assembly_model_xml.appendChild(model_ID_xml)
        
        
        grid_xml=doc.createElement('spacer_grid_mat')
        fix_grid=self.grids.filter(functionality='fix').first()
        grid_xml.appendChild(doc.createTextNode(fix_grid.sleeve_material.prerobin_identifier))
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
        
        
        
    def generate_pin_xml(self):
        doc = minidom.Document()
        pin_xml=doc.createElement('pin_databank')
        doc.appendChild(pin_xml)
        #FEUL PIN
        fuel_elements=self.fuel_elements.all()
        
        for fuel_element in fuel_elements:
            fuel_xml=fuel_element.generate_base_pin_xml()
            pin_xml.appendChild(fuel_xml)
            
        #instrument pin
        instrument_tube=self.instrument_tube
        instrument_xml=instrument_tube.generate_base_pin_xml()
        pin_xml.appendChild(instrument_xml)  
        
        #guide tube
        guide_tube=self.guide_tube
        guide_xml=guide_tube.generate_base_pin_xml()
        pin_xml.appendChild(guide_xml)
         
        #bp rod
        bp_rod=self.bp_rod
        bp_rod_xml=bp_rod.generate_base_pin_xml()
        pin_xml.appendChild(bp_rod_xml)
         
        f=open('/home/django/Desktop/pin_databank.xml','w')   
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        f.close()
        
    def __str__(self):
        return "{}".format(self.name)

class FuelAssemblyType(BaseModel):
    model=models.ForeignKey(FuelAssemblyModel)
    assembly_enrichment=models.DecimalField(max_digits=4, decimal_places=3,validators=[MinValueValidator(0)],help_text='meaningful only if using the one unique enrichment fuel',blank=True,null=True)
    map=models.ManyToManyField('FuelElementType',through='FuelElementTypePosition')
    symmetry=models.BooleanField(default=True,help_text="satisfy 1/8 symmetry")
    class Meta:
        db_table='fuel_assembly_type'
        
    @property
    def side_pin_num(self):
        return self.model.side_pin_num
    
    @property
    def height_lst(self):
        rods=self.map.all()
        height_set=set()
        for rod in rods:
            rod_set=set(rod.height_lst)
            height_set=height_set|rod_set
        height_lst=sorted(list(height_set))
        return height_lst
    
    def generate_transection(self,height,fuel=False):
        if self.symmetry:
            rod_positions=self.rod_positions.all()
            transection={}
            for rod_position in rod_positions:
                if rod_position.in_triangle:
                    row=rod_position.row
                    column=rod_position.column
                    #get the fuel element
                    fet=rod_position.fuel_element_type
                    rod_transection_pk=fet.which_transection(height,fuel=fuel)
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
                
    def generate_assembly_model_xml(self):
        assembly_model_xml=self.model.generate_assembly_model_xml()
        fuel_map_xml=self.generate_fuel_map_xml()
        pin_map_xml=self.generate_pin_map_xml()
        assembly_model_xml.appendChild(pin_map_xml)  
        assembly_model_xml.appendChild(fuel_map_xml)  
        
        doc=minidom.Document()
        doc.appendChild(assembly_model_xml)
        f=open('/home/django/Desktop/assembly_model.xml','w')
        doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        f.close() 
        
    def __str__(self):
        return "{} {} {}".format(self.pk,self.model,self.assembly_enrichment)  
    

    
class FuelAssemblyRepository(BaseModel):
    PN=models.CharField(max_length=50,blank=True,null=True)
    type=models.ForeignKey(FuelAssemblyType)
    batch_number=models.PositiveSmallIntegerField(blank=True,null=True)
    manufacturing_date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True)
    arrival_date=models.DateField(help_text='Please use <b>YYYY-MM-DD<b> to input the date',blank=True,null=True)
    vendor=models.ForeignKey(Vendor,default=1)
    availability=models.BooleanField(default=True)
    broken=models.BooleanField(default=False)
    unit=models.ForeignKey(UnitParameter,related_name='fuel_assemblies',blank=True,null=True)
    
    class Meta:
        db_table='fuel_assembly_repository'
        verbose_name_plural='Fuel assembly repository'
        
    @staticmethod
    def autocomplete_search_fields():
        return ("pk__iexact", "PN__icontains",)
    
    
        
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
            bpa_pattern=BurnablePoisonAssemblyLoadingPattern.objects.get(cycle=first_cycle,reactor_position=first_position)
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
        mid_pos=FuelAssemblyPosition.objects.get(type='instrument',fuel_assembly_model=self.fuel_assembly_model)
        mid_row=mid_pos.row
        mid_column=mid_pos.column
        if row<=mid_row:
            if column<=mid_column:
                return 1
            else:
                return 2
        else:
            if column<=mid_column:
                return 3
            else:
                return 4
        
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
        2|1
        ---
        3|4
        the lower triangle of quadrant 4
        '''
        side_num=self.fuel_assembly_type.side_pin_num 
        half=int(side_num/2)+1
        row=self.row
        column=self.column
        if row>=half and column>=half and column<=row:
            return True
        else:
            return False
        
    def __str__(self):
        return '{} {}'.format(self.fuel_element_type,self.fuel_assembly_position)
    



class GridPosition(BaseModel):
    fuel_assembly_model=models.ForeignKey(FuelAssemblyModel,related_name='grid_pos')
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
    side_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',blank=True,null=True)
    sleeve_height=models.DecimalField(max_digits=15, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm')
    inner_sleeve_thickness=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',blank=True,null=True)
    outer_sleeve_thickness=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',blank=True,null=True)
    sleeve_material=models.ForeignKey(Material,related_name='grid_sleeves',related_query_name='grid_sleeve',blank=True,null=True)
    spring_thickness=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='cm',blank=True,null=True)
    spring_material=models.ForeignKey(Material,related_name='grid_springs',related_query_name='grid_spring',blank=True,null=True)
    functionality=models.CharField(max_length=5,choices=FUCTIONALITY_CHOICS,default='fix')
    
    
    class Meta:
        db_table='grid'
        verbose_name='Fuel grid'
    
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
        
    def generate_base_pin_xml(self):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID='GT'
        radii="{},{}".format(self.upper_inner_diameter,self.upper_outer_diameter)
        mat='MOD,'+self.material.prerobin_identifier
        
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
        
    def generate_base_pin_xml(self):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID='IT'
        radii="{},{}".format(self.inner_diameter,self.outer_diameter)
        mat='MOD,'+self.material.prerobin_identifier
        
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
    #plenum_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #filling_gas_pressure=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:MPa',blank=True,null=True)
    #filling_gas_material=models.ForeignKey(Material,related_name='filling_fuel_elements',default=46)
    #radial_map=models.ManyToManyField(Material,through='FuelElementRadialMap')
    #handle the coating material like IFBA
    #coated=models.BooleanField(default=False,help_text="whether coated with some materials")
    #coating_thickness=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #coating_material=models.ForeignKey(Material,related_name='coating_fuel_elements',blank=True,null=True)
    #coating_bottom=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm based on the bottom of the active part',blank=True,null=True)
    #coating_top=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm based on the bottom of the active part',blank=True,null=True)
    
    class Meta:
        db_table='fuel_element'
  
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
        return "{} fuel element".format(self.fuel_assembly_model)
    
class FuelElementSection(BaseModel):
    '''
    no containing fuel description
    '''
    fuel_element=models.ForeignKey(FuelElement,related_name='sections')
    section_num=models.PositiveSmallIntegerField()
    length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm')
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
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID=self.pin_id
        radial_map=self.material_transection.radial_materials.order_by('radius')
        radii_tup,mat_tup=zip(*[(str(item.radius),item.material.prerobin_identifier) for item in radial_map])
  
        radii_lst=list(radii_tup)
        mat_lst=list(mat_tup)
        
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
    
class MaterialTransection(BaseModel):
    radius=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    radial_map=models.ManyToManyField(Material,through='TransectionMaterial')
    
    class Meta:
        db_table='material_transection'
        
    @property
    def pin_id(self):
        if self.if_fuel:
            return "FUEL_"+str(self.pk)
        else:
            return "BP_"+str(self.pk)
    
    
    @property
    def if_fuel(self):
        materials=self.radial_map.all()
        if "FUEL" in [str(material) for material in materials]:
            return True
        else:
            return False
        
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
    
    def which_transection(self,height,fuel=False):
        #if fuel return material pk
        #else return material transection object
        if fuel:
            section_num=self.which_section(height=height,fuel=True) 
            pellet_section=self.fuel_pellet_map.get(section_num=section_num)
            fuel_pellet_type=pellet_section.fuel_pellet_type
            return fuel_pellet_type.material.pk
       
        return self.model.which_transection(height)
    
    @property
    def enrichment(self):
        try:
            pellet_pos=self.pellet.get()
            return pellet_pos.enrichment
        except:
            return None
        
    def __str__(self):
        obj=FuelElementType.objects.get(pk=self.pk)
        ctr=obj.fuel_pellet_map.all().first()
        if  ctr:
            fp=ctr.fuel_pellet_type
            mt=fp.material
            
        else:
            mt=''
        
        return "{} {} {}".format(self.pk,self.model,mt)
    
    
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
    fuel_assembly_model=models.OneToOneField(FuelAssemblyModel)
    outer_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    inner_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],blank=True,null=True,help_text='unit:cm can be none when hollow')
    length=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    dish_volume_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",blank=True,null=True)
    chamfer_volume_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",blank=True,null=True)
    dish_depth=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    dish_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    roughness=models.DecimalField(max_digits=7, decimal_places=6,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    nominal_density=models.DecimalField(max_digits=8, decimal_places=5,validators=[MinValueValidator(0)],help_text=r"unit:g/cm3")
    uncertainty_percentage=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(0)],help_text=r"unit:%",blank=True,null=True)  
    coating_thickness=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    coating_material=models.ForeignKey(Material,related_name='fuel_pellet_coating',blank=True,null=True)
    
    class Meta:
        db_table='fuel_pellet'
        
    def __str__(self):
        return '{} pellet'.format(self.fuel_assembly_model)

class FuelPelletType(BaseModel):
    model=models.ForeignKey(FuelPellet)
    material=models.ForeignKey(Material,related_name='fuel_pellet_material')
    
    class Meta:
        db_table='fuel_pellet_type'
        
    @property
    def enrichment(self):
        return self.material.enrichment
        
    def __str__(self):
        return '{} {} {}'.format(self.pk,self.model,self.material)
    
    
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
    #fuel_assembly_model=models.ForeignKey(FuelAssemblyModel)
    reactor_model=models.ForeignKey(ReactorModel,blank=True,null=True)
    active_length=models.DecimalField(max_digits=7, decimal_places=3,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)  
    #absorb_material=models.ForeignKey(Material,related_name='control_rod_absorb')
    #absorb_length=models.DecimalField(max_digits=9, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    #absorb_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    #cladding_material=models.ForeignKey(Material,related_name='control_rod_cladding')
    #cladding_inner_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    #cladding_outer_diameter=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    radial_map=models.ManyToManyField(Material,through='ControlRodRadialMap')
    class Meta:
        db_table='control_rod_type'
        verbose_name='Control rod'
        
    @property
    def base_pin_id(self):
        return 'CR_'+str(self.pk)
    
    def generate_base_pin_xml(self,fuel_assembly_model):
        doc=minidom.Document()
        base_pin_xml=doc.createElement('base_pin')
        ID=self.base_pin_id
        radial_map=self.radial_materials.order_by('radii')
        radii_tup,mat_tup=zip(*[(str(item.radii),item.material.prerobin_identifier) for item in radial_map])
  
        #insert into guide tube
        guide_tube=fuel_assembly_model.guide_tube
        radii_lst=list(radii_tup)
        radii_lst.append(str(guide_tube.upper_inner_diameter))
        radii_lst.append(str(guide_tube.upper_outer_diameter))
        mat_lst=list(mat_tup)
        mat_lst.append('MOD')
        mat_lst.append(guide_tube.material.prerobin_identifier)
        
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
    @property
    def black(self):
        materials=self.radial_map.all()
        #AIC
        AIC=Material.objects.get(pk=7)
        if AIC in materials:
            return True
        else:
            return False
        
    def __str__(self):
        if self.black:
            return '{} black rod'.format(self.reactor_model)
        else:
            return '{} grey rod'.format(self.reactor_model)
    
class ControlRodRadialMap(BaseModel):
    control_rod=models.ForeignKey(ControlRodType,related_name='radial_materials')
    radii=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    material=models.ForeignKey(Material)
    
    class Meta:
        db_table='control_rod_radial_map'
        
    def __str__(self):
        return "{} radial map".format(self.control_rod)
    
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
    length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],blank=True,null=True,help_text='unit:cm')
    active_length=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm') 
    bottom_height=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm based on the bottom of fuel active part')                 
    class Meta:
        db_table='burnable_poison_rod'
        #verbose_name='Burnable absorber rod'
    @property
    def height_lst(self):
        sections=self.sections.all()
        height_lst=[section.bottom_height for section in sections]
        return height_lst
    
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
        if section_num==0:
            return 0
        else:
            section=self.sections.get(section_num=section_num)
            return section.material_transection.pk
    def __str__(self):
        return '{} burnable poison rod'.format(self.fuel_assembly_model)


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
        radii_tup,mat_tup=zip(*[(str(item.radius),item.material.prerobin_identifier) for item in radial_map])
  
        #insert into guide tube
        radii_lst=list(radii_tup)
        radii_lst.append(str(guide_tube.upper_inner_diameter))
        radii_lst.append(str(guide_tube.upper_outer_diameter))
        mat_lst=list(mat_tup)
        mat_lst.append('MOD')
        mat_lst.append(guide_tube.material.prerobin_identifier)
        
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
    
    
    def generate_transection(self,height):
        if self.symmetry:
            rod_positions=self.rod_positions.all()
            transection={}
            for rod_position in rod_positions:
                if rod_position.in_triangle:
                    row=rod_position.row
                    column=rod_position.column
                    bpr=rod_position.burnable_poison_rod
                    rod_transection_pk=bpr.which_transection(height)
                    #has bpa at this height
                    if rod_transection_pk!=0:
                        transection[(row,column)]=rod_transection_pk
            return transection
        else:
            return None
    
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
        
        return symbol_lst
    
    def get_substitute_bpa(self):
        quadrant_symbol=self.get_quadrant_symbol()
        if quadrant_symbol==[1,2,3,4]:
            return None
        else:
            num=self.get_poison_rod_num()
            sub_num=num*4/len(quadrant_symbol)
            sub_bpas=BurnablePoisonAssembly.objects.filter(fuel_assembly_model=self.fuel_assembly_model)
            for sub_bpa in sub_bpas:
                if sub_bpa.get_poison_rod_num()==sub_num:
                        return sub_bpa
            
    def __str__(self):
        num=self.rod_positions.count()
        return '{} {}'.format(num, self.fuel_assembly_model)

class BurnablePoisonAssemblyMap(BaseModel):
    burnable_poison_assembly=models.ForeignKey(BurnablePoisonAssembly,related_name='rod_positions')
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    burnable_poison_rod=models.ForeignKey(BurnablePoisonRod)
    
    class Meta:
        db_table='burnable_poison_assembly_map'
            
    @property    
    def position(self):
        return self.burnable_poison_assembly.fuel_assembly_model.positions.get(row=self.row,column=self.column)
    
    @property
    def in_triangle(self):
        '''to check if this position is in the 1/8 part to be calculated
        2|1
        ---
        3|4
        the lower triangle of quadrant 4
        '''
        side_num=self.burnable_poison_assembly.side_pin_num 
        half=int(side_num/2)+1
        row=self.row
        column=self.column
        if row>=half and column>=half and column<=row:
            return True
        else:
            return False
    
    def __str__(self):
        return "{} R{}C{}".format(self.burnable_poison_assembly,self.row,self.column)
    

class BurnablePoisonAssemblyLoadingPattern(BaseModel):
    
    cycle=models.ForeignKey(Cycle,related_name='bpa_loading_patterns')
    reactor_position=models.ForeignKey(ReactorPosition)
    burnable_poison_assembly=models.ForeignKey(BurnablePoisonAssembly)
    
    

    class Meta:
        db_table='burnable_poison_assembly_loading_pattern'
        
        #unique_together=('reactor_position','burnable_poison_assembly')
        #verbose_name='Burnable absorber assembly'
        #verbose_name_plural='Burnable absorber assemblies'
        
    def clean(self):
        if self.cycle.unit.reactor_model !=self.reactor_position.reactor_model:
            raise ValidationError({'cycle':_('the cycle and reactor_position are not compatible'),
                                   'reactor_position':_('the cycle and reactor_position are not compatible')
                                   
            }) 
        
    def get_sysmetry_quadrant(self):
        reactor_position=self.reactor_position
        reactor_position_symbol=reactor_position.get_quadrant_symbol()
        bpa=self.burnable_poison_assembly
        bpa_symbol=bpa.get_quadrant_symbol()
        if reactor_position_symbol==4:
            sysm_relation={1:1,2:2,3:3,4:4}
        elif reactor_position_symbol==1: 
            sysm_relation={3:1,1:2,4:3,2:4}
        elif reactor_position_symbol==2:
            sysm_relation={4:1,3:2,2:3,1:4}
        else:
            sysm_relation={2:1,4:2,1:3,3:4}
            
        sysmetry_quadrant=[sysm_relation[i] for i in bpa_symbol]
        return sysmetry_quadrant
            
    def __str__(self):
        return '{} {}'.format(self.cycle, self.reactor_position)
    
    
    
###############################################################################

class ControlRodAssemblyType(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel,related_name='cra_types')
    basez=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    step_size=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    side_pin_num=models.PositiveSmallIntegerField(default=17)
    map=models.ManyToManyField(ControlRodType,through='ControlRodAssemblyMap')
    symmetry=models.BooleanField(default=True,help_text="satisfy 1/8 symmetry")
    class Meta:
        db_table='control_rod_assembly_type'
        
    @property
    def type(self):
        #1 represents black rod
        #2 represents grep rod
        control_rods=self.map.all()
        for control_rod in control_rods:
            if not control_rod.black:
                return 2
        return 1
    
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
    def base_branch_id(self):
        return 'BRCH_'+'CRD_'+str(self.pk)
    
    def generate_base_branch_xml(self): 
        side_num=self.side_pin_num 
        half=int(side_num/2)+1
        control_rod_pos=self.control_rod_pos.all()
        CRD='\n'
        for row in range(half,side_num+1):
            row_lst=[]
            for col in range(half,row+1):
                if control_rod_pos.filter(row=row,column=col).exists():
                    control_rod_id=control_rod_pos.get(row=row,column=col).control_rod_type.base_pin_id
                         
                else:   
                    control_rod_id='NONE'
                row_lst.append(control_rod_id)
        
            CRD +=('  '.join(row_lst)+'\n')
            
        ID=self.base_branch_id
        doc=minidom.Document()
        base_branch_xml=doc.createElement('base_branch')
        
        ID_xml=doc.createElement('ID')
        ID_xml.appendChild(doc.createTextNode(ID))
        base_branch_xml.appendChild(ID_xml)
        
        CRD_xml=doc.createElement('CRD')
        CRD_xml.appendChild(doc.createTextNode(CRD))
        base_branch_xml.appendChild(CRD_xml)
        
        #doc.appendChild(base_branch_xml)
        #f=open('/home/django/Desktop/branch_crd.xml','w')
        #doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
        #f.close()
        return base_branch_xml
    
    def __str__(self):
        return '{} {}'.format(self.reactor_model,self.type)

class ControlRodAssemblyMap(BaseModel):
    control_rod_assembly_type=models.ForeignKey(ControlRodAssemblyType,related_name='control_rod_pos')
    #guide_tube_position=models.ForeignKey(FuelAssemblyPosition,limit_choices_to={'type': 'guide'})
    row=models.PositiveSmallIntegerField()
    column=models.PositiveSmallIntegerField()
    control_rod_type=models.ForeignKey(ControlRodType)
    
    
    class Meta:
        db_table='control_rod_assembly_map'
        #unique_together=('control_rod_assembly','guide_tube_position')
    def clean(self):
        side_pin_num=self.control_rod_assembly_type.side_pin_num
        if self.row>side_pin_num:
            raise ValidationError({'row':_('the row or column is bigger than side pin number'),                         
            })
        if self.column>side_pin_num:
            raise ValidationError({'column':_('the column is bigger than side pin number'),                     
            })
        #if self.control_rod_type.reactor_model!=self.control_rod_assembly_type.reactor_model:
        #    raise ValidationError({'control_rod_type':_('the control_rod_type is not correct'),                     
        #    })
    def __str__(self):
        return '{} {}'.format(self.control_rod_assembly_type,self.control_rod_type)
  
    
class ControlRodCluster(BaseModel):
    reactor_model=models.ForeignKey(ReactorModel,related_name='control_rod_clusters')
    control_rod_assembly_type=models.ForeignKey(ControlRodAssemblyType,related_name='clusters')
    cluster_name=models.CharField(max_length=5)
    #basez=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #step_size=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm',blank=True,null=True)
    #side_pin_num=models.PositiveSmallIntegerField(default=17)
    #map=models.ManyToManyField(ControlRodType,through='ControlRodMap')
    class Meta:
        db_table='control_rod_cluster'
        
    def get_control_rod_assembly_num(self):
        return self.control_rod_assemblies.count()
    get_control_rod_assembly_num.short_description='same cluster number'
    
    
    @property
    def type(self):
        #1 represents black rod
        #2 represents grep rod
        return self.control_rod_assembly_type.type
    
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
        return '{}'.format(self.cluster_name)
    
#the following two models describe control rod assembly
class ControlRodAssembly(BaseModel):
    TYPE_CHOICES=(
                  (1,'black rod'),
                  (2,'grey rod'),
    )
    cluster=models.ForeignKey(ControlRodCluster,related_name='control_rod_assemblies',blank=True,null=True)
    #type=models.PositiveSmallIntegerField(default=1,choices=TYPE_CHOICES)
    #basez=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    #step_size=models.DecimalField(max_digits=7, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:cm')
    #primary=models.BooleanField(default=False,verbose_name='if primary?')
    #control_rod_map=models.ManyToManyField(FuelAssemblyPosition,through='ControlRodMap')
    
    class Meta:
        db_table='control_rod_assembly'
       
        verbose_name_plural='Control rod assemblies'
        
    @property
    def cluster_name(self):
        return self.cluster.cluster_name
    @property
    def type(self):
        return self.cluster.type
    @property
    def reactor_model(self):
        return self.cluster.reactor_model
    
    @property
    def step_size(self):
        return self.cluster.step_size
    @property
    def basez(self):
        return self.cluster.basez
        
    def __str__(self):
        return '{} {}'.format(self.pk,self.cluster)

       
class ControlRodAssemblyLoadingPattern(BaseModel):
    cycle=models.ForeignKey(Cycle,related_name='control_rod_assembly_loading_patterns',blank=True,null=True)
    reactor_position=models.ForeignKey(ReactorPosition,related_name='control_rod_assembly_pattern',)
    control_rod_assembly=models.ForeignKey(ControlRodAssembly,related_name='loading_patterns',)
    
    

    class Meta:
        db_table='control_rod_assembly_loading_pattern'
        
    def clean(self):
        if self.cycle.unit.reactor_model !=self.reactor_position.reactor_model:
            raise ValidationError({'cycle':_('the cycle and reactor_position are not compatible'),
                                   'reactor_position':_('the cycle and reactor_position are not compatible')
                                   
            })
        
    
    def __str__(self):
        return '{} '.format(self.reactor_position)    
    

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
    axial_power_shift=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    control_rod_step=models.ManyToManyField(ControlRodCluster,through='ControlRodAssemblyStep')
    
    class Meta:
        db_table='operation_daily_parameter'
        order_with_respect_to = 'cycle'
        
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
    
    @classmethod
    def generate_cycle_calc_xml(cls,pk_lst):
        doc = minidom.Document()
        isq=1
        cycle_calc_xml=doc.createElement('cycle_calc')
        
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
    axial_power_shift=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    #FDH=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:')
    FQ=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:',blank=True,null=True)
    raw_file=models.FileField(upload_to=get_monthly_data_upload_path,)
    bank_position=models.ManyToManyField(ControlRodCluster,through='OperationBankPosition')
    distribution=models.ManyToManyField(ReactorPosition,through='OperationDistributionData')
    
    class Meta:
        db_table='operation_monthly_parameter'
        order_with_respect_to = 'cycle'
             
    def __str__(self):
        return "{}".format(self.cycle,)
    
class OperationBankPosition(BaseModel):
    operation=models.ForeignKey(OperationMonthlyParameter)
    control_rod_cluster=models.ForeignKey(ControlRodCluster)
    step=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)])
    
    class Meta:
        db_table='operation_bank_position'
        order_with_respect_to = 'operation'
        
    def __str__(self):
        return "{}".format(self.operation,)
    
    
    
class OperationDistributionData(BaseModel):
    operation=models.ForeignKey(OperationMonthlyParameter)
    reactor_position=models.ForeignKey(ReactorPosition)
    relative_power=models.DecimalField(max_digits=10, decimal_places=9,validators=[MinValueValidator(0),MaxValueValidator(1)],)
    FDH=models.DecimalField(max_digits=10, decimal_places=5,validators=[MinValueValidator(0)],help_text='unit:')
    axial_power_shift=models.DecimalField(max_digits=9, decimal_places=6,validators=[MaxValueValidator(100),MinValueValidator(-100)],help_text=r"unit:%FP",blank=True,null=True)
    
    class Meta:
        db_table='operation_distribution_data'
        order_with_respect_to = 'operation'
    def __str__(self):
        return "{}".format(self.operation,)
    
    
