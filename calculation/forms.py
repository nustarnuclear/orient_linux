'''
Created on Mar 16, 2016

@author: django
'''
from django import forms
from tragopan.models import UnitParameter,ReactorModel

class UnitForm(forms.Form):
    unit=forms.ModelChoiceField(label='Select Unit',queryset=UnitParameter.objects.all(), empty_label=None)

class ReactorModelForm(forms.Form):
    reactor_model=forms.ModelChoiceField(label='Select Reactor model',queryset=ReactorModel.objects.all(), empty_label=None)   