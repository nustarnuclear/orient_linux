'''
Created on Mar 16, 2016

@author: django
'''
from django import forms
from tragopan.models import UnitParameter,ReactorModel
from django.core.validators import MinValueValidator,MaxValueValidator
class UnitForm(forms.Form):
    unit=forms.ModelChoiceField(label='Select Unit',queryset=UnitParameter.objects.all(), empty_label=None)

class ReactorModelForm(forms.Form):
    reactor_model=forms.ModelChoiceField(label='Select Reactor model',queryset=ReactorModel.objects.all(), empty_label=None)   
    
class EgretDefaultForm(forms.Form):
    subdivision_CHOICES=(
                         ('2','2'),
    )
    num_radial_brs_CHOICES=(
                            ('2','2'),
    )
    fold_core_CHOICES=(
                       ('1','1'),
    )
    axial_df_CHOICES=(
                      ('0','0'),
                      ('1','1'),
    )
    unit=forms.ModelChoiceField(label='Select Unit',queryset=UnitParameter.objects.all(), empty_label=None)
    subdivision=forms.ChoiceField(choices=subdivision_CHOICES)
    num_radial_brs=forms.ChoiceField(choices=num_radial_brs_CHOICES)
    bot_br_size=forms.DecimalField(initial=19.251)
    top_br_size=forms.DecimalField(initial=19.251)
    fold_core=forms.ChoiceField(choices=fold_core_CHOICES)
    axial_df=forms.ChoiceField(choices=axial_df_CHOICES)
    axial_mesh=forms.DecimalField(initial=20)
    cyclen_std_bu=forms.CharField(max_length=128,initial='50.0 150.0 500.0 1000.0 2000.0 3000.0 5000.0 7000.0 10000.0 13000.0 16000.0 20000.0 24000.0 28000.0',widget=forms.Textarea)
    
class PowerTemperatureForm(forms.Form):
    relative_power=forms.DecimalField(validators=[MinValueValidator(0),MaxValueValidator(1)])
    inlet_temperature=forms.DecimalField()