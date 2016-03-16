'''
Created on Mar 16, 2016

@author: django
'''
from django import forms
from tragopan.models import UnitParameter

class UnitForm(forms.Form):
    unit=forms.ModelChoiceField(label='Select Unit',queryset=UnitParameter.objects.all(), empty_label=None)
    