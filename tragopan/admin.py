from django.contrib import admin
from .models import *
from django.db.models import Sum,F,Count
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
# Register your models here.

#################################################
#basic information 
#################################################

#element information

class NuclideInline(admin.TabularInline):
    model=Nuclide
    extra=0
    exclude=('reference','remark')
    #list_display=('__str__','atom_mass','abundance',)
    readonly_fields=('atom_mass','abundance')
    
    
        
class ElementAdmin(admin.ModelAdmin):
    
    fieldsets=[
               (None,{'fields':['atomic_number','symbol']}),
               ('Element information',{'fields':['nameCH','nameEN'],'classes': ['collapse']})
             ]
    inlines=[NuclideInline]
    search_fields=('=symbol',)
    readonly_fields=('atomic_number','symbol','nameCH','nameEN')
    list_display=('atomic_number','symbol','nameCH','nameEN','element_average_mass','get_isotopes_num','is_correct',)
    list_display_links=('atomic_number','symbol','nameCH','nameEN')
    
    #calculate the average mass of each element
    def element_average_mass(self,obj):
        element_mass=obj.nuclides.all().aggregate(avg_mass=Sum(F('atom_mass')*F('abundance')/100))
        if element_mass['avg_mass']==0:
            return 'Non Existent in nature'
        return str(round(element_mass['avg_mass'],5))       
    element_average_mass.short_description='Element Mass'
    
    #get the natural existent isotopes number of each element
    def get_isotopes_num(self,obj):
        isotopes=obj.nuclides.filter(abundance__gt=0).aggregate(num_isotopes=Count('id'))
        return isotopes['num_isotopes']
    get_isotopes_num.short_description='Natural Existent Isotopes Count'
    
    #check if satisfy the integrity constraint
    def is_correct(self,obj):
        pecentage_sum=obj.nuclides.all().aggregate(sum=Sum('abundance'))
        if pecentage_sum['sum'] in [100,0]:
            return True
        return False
    is_correct.short_description='Data Integrity?'
    is_correct.boolean=True       
admin.site.register(Element, ElementAdmin)

class NuclideAdmin(admin.ModelAdmin):
    exclude=('reference','remark')
    search_fields=('=element__symbol',)
    ordering=('element','atom_mass')
    list_display=('__str__','atom_mass','abundance')
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('element','atom_mass','abundance')
        return ()    
    
    # define the raw_id_fields
    #raw_id_fields = ('element',)
    # define the autocomplete_lookup_fields
    #autocomplete_lookup_fields = {
    #    'fk': ['element'],
    #}
admin.site.register(Nuclide, NuclideAdmin)

class WimsNuclideDataAdmin(admin.ModelAdmin):
    list_display=('__str__','element','id_wims','id_self_defined','amu','nf','material_type','descrip','res_trig','dep_trig')
    #list_editable=('id_self_defined',)
    ordering=('time_inserted',)
    list_filter=('element','id_wims','nf','material_type')
    search_fields=('=id_wims','=element__symbol',)
    raw_id_fields = ('element',)
    autocomplete_lookup_fields = {
        'fk': ['element',],
    }
admin.site.register(WimsNuclideData, WimsNuclideDataAdmin)   

class WmisElementCompositionInline(admin.TabularInline):
    model=WmisElementComposition
    exclude=('remark',)
    extra=0

class WmisElementDataAdmin(admin.ModelAdmin):
    ordering=('time_inserted',)
    exclude=('remark',)
    inlines=[WmisElementCompositionInline,]
    list_display=('__str__','get_nuclide_num','is_correct',)
    #check if satisfy the integrity constraint
    def is_correct(self,obj):
        cps=obj.nuclides.all()
        pecentage_sum=0
        for cp in cps:
            pecentage_sum +=cp.weight_percent
            
        if pecentage_sum==100:
            return True
        return False
    is_correct.short_description='Data Integrity?'
    is_correct.boolean=True  
    
admin.site.register(WmisElementData, WmisElementDataAdmin) 

'''
#material information
class MaterialCompositionInline(admin.TabularInline):
    model=MaterialComposition
    exclude=('remark',)
    raw_id_fields = ('wims_element_data',)
    # define the related_lookup_fields
    autocomplete_lookup_fields = {
        'fk': ['wims_element_data',],
    }
    related_lookup_fields = {
        'fk': ['wims_element_data',],
        
    }
    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            return extra-1
        return extra
'''
#mixture information
class MixtureCompositionInline(admin.TabularInline):
    model=MixtureComposition
    exclude=('remark',)
    fk_name='mixture'
    extra=0


class MaterialAttributeInline(admin.TabularInline):
    model=MaterialAttribute
    extra=1
    exclude=('remark',)
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('density','heat_capacity','thermal_conductivity','expansion_coefficient','code')

        return ()
    
class BasicElementCompositionInline(admin.TabularInline):
    model=BasicElementComposition
    extra=3
    exclude=('remark',)
    
    # define the related_lookup_fields
    raw_id_fields = ('wims_element',)
    autocomplete_lookup_fields = {
        'fk': ['wims_element',],
    }
    related_lookup_fields = {
        'fk': ['wims_element',],
        
    }

class BasicMaterialAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','type','get_element_num','data_integrity')
    #list_editable=('type',)
    inlines=(BasicElementCompositionInline,)
admin.site.register(BasicMaterial,BasicMaterialAdmin)

class MaterialAdmin(admin.ModelAdmin):
    inlines=(MaterialAttributeInline,MixtureCompositionInline)
    exclude=('remark',)
    list_display=('__str__','input_method')
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('nameEN','nameCH')
        return ()
admin.site.register(Material, MaterialAdmin)


class VendorResource(resources.ModelResource):

    class Meta:
        model = Vendor
        import_id_fields = ('nameCH',)
        fields=('nameCH','nameEN','abbrCH','abbrEN','type')
        export_order = ('type','nameCH','nameEN','abbrCH','abbrEN',)

class VendorAdmin(ImportExportModelAdmin):
    resource_class = VendorResource
    exclude=('remark',)
    list_display=('pk','nameEN','nameCH','type')
    list_display_links=('nameEN','nameCH')
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('nameCH','nameEN','abbrCH','abbrEN','type')
        return ()
admin.site.register(Vendor, VendorAdmin)

#################################################
#nuclear power plant basic information 
#################################################
class UnitParameterInline(admin.TabularInline):
    model=UnitParameter
    exclude=('remark',)
    extra=0
    #show_change_link=True



        
class PlantAdmin(admin.ModelAdmin):
  
    
    exclude=('remark',)
    list_display=('nameEN','nameCH','get_unit_num')
    list_display_links=('nameEN','nameCH')
    inlines=(UnitParameterInline,)
    
    #def get_readonly_fields(self,request, obj=None):
    #    if not request.user.is_superuser:
    #        return ('nameCH','nameEN','abbrCH','abbrEN')
    #    return ()
    
    def get_unit_num(self,obj):
        unit_num=obj.units.count()
        return unit_num
    get_unit_num.short_description='unit number'
admin.site.register(Plant, PlantAdmin)

class ReactorPositionAdmin(admin.ModelAdmin):
    exclude=('remark',)
    search_fields=('=row','=column')
    list_filter=('reactor_model__name',)
    list_display=('reactor_model','__str__','control_rod_cluster','get_quadrant_symbol')
    list_per_page=200
    ordering=('row','column')
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('reactor_model','row','column')
        return ()
admin.site.register(ReactorPosition, ReactorPositionAdmin)

#the following inline tables describe a kind of reactor model
class ReactorPositionInline(admin.TabularInline):
    model=ReactorPosition
    exclude=('remark',)
    
    def get_extra(self, request, obj=None, **kwargs):
        extra = 121
        if obj:
            extra -= obj.positions.count()
        return extra
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('row','column',)
        return ()

class CoreBarrelInline(admin.TabularInline):
    model=CoreBarrel
    extra=1
    exclude=('remark',)
    verbose_name_plural='core barrel'
    
class CoreUpperPlateInline(admin.TabularInline):
    model=CoreUpperPlate
    extra=1
    exclude=('remark',)
    verbose_name_plural='core upper plate'
    
class CoreLowerPlateInline(admin.TabularInline):
    model=CoreLowerPlate
    extra=1
    exclude=('remark',)
    verbose_name_plural='core lower plate'
    
class ThermalShieldInline(admin.TabularInline):
    model=ThermalShield
    extra=1
    exclude=('remark',)

class PressureVesselInline(admin.TabularInline):
    model=PressureVessel
    extra=1
    exclude=('remark',)
    verbose_name_plural='pressure vessel'
    
class PressureVesselInsulationInline(admin.TabularInline):
    model=PressureVesselInsulation
    extra=1
    exclude=('remark',)
    verbose_name_plural='pressure vessel insulation'
    
class CoreBaffleInline(admin.TabularInline):
    model=CoreBaffle
    extra=1
    exclude=('remark',)
    verbose_name_plural='core baffle'

class ThermalCouplePositionInline(admin.TabularInline):
    model = ReactorModel.thermal_couple_position.through
    verbose_name='thermal_couple_position'
    verbose_name_plural='thermal couple position'
    
    def get_extra(self, request, obj=None, **kwargs):
        extra =30
        if obj:
            extra -= obj.thermal_couple_position.count()
        return extra
    

class IncoreInstrumentPositionInline(admin.TabularInline):
    model = ReactorModel.incore_instrument_position.through
    verbose_name='incore_instrument_position'
    verbose_name_plural='incore instrument position'
    
    def get_extra(self, request, obj=None, **kwargs):
        extra =38
        if obj:
            extra -= obj.incore_instrument_position.count()
        return extra
    
class ReactorModelAdmin(admin.ModelAdmin):
    exclude=('remark','thermal_couple_position','incore_instrument_position')
    inlines=[CoreBaffleInline,CoreUpperPlateInline,CoreLowerPlateInline,ThermalShieldInline,PressureVesselInline,PressureVesselInsulationInline,CoreBaffleInline,
             ]
    #raw_id_fields=('thermal_couple_position','incore_instrument_position')
    list_display=['name','generation','reactor_type','get_thermal_couple_num','get_incore_instrument_num','get_fuel_assembly_num','get_max_row_column']
    
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if not request.user.is_superuser:
                if isinstance(inline, ThermalCouplePositionInline) or isinstance(inline, IncoreInstrumentPositionInline):
                    continue
            yield inline.get_formset(request, obj), inline
    
    def get_thermal_couple_num(self,obj):
        num=obj.thermal_couple_position.count()
        return num
    get_thermal_couple_num.short_description='thermal couple count'
    
    def get_incore_instrument_num(self,obj):
        num=obj.incore_instrument_position.count()
        return num
    get_incore_instrument_num.short_description='incore instrument count'
    
    
    def get_fuel_assembly_num(self,obj):
        num=obj.positions.count()
        return num
    get_fuel_assembly_num.short_description='fuel assembly count'
    
      
admin.site.register(ReactorModel,ReactorModelAdmin)

class UnitParameterAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','get_current_cycle','base_component_path','base_core_path','loading_pattern_path',)
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('plant','unit','reactor_model','electric_power','thermal_power','heat_fraction_in_fuel','primary_system_pressure',
                    'ave_linear_power_density','ave_vol_power_density','ave_mass_power_density','best_estimated_cool_vol_flow_rate','bypass_flow_fraction',
                    'cold_state_cool_temp','HZP_cool_inlet_temp','HFP_cool_inlet_temp','HFP_core_ave_cool_temp','mid_power_cool_inlet_temp',)
        return ()
admin.site.register(UnitParameter, UnitParameterAdmin)

#plant operation information
class FuelAssemblyLoadingPatternInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelAssemblyLoadingPattern
    extra=0
    raw_id_fields = ("fuel_assembly",)

class FuelAssemblyLoadingPatternAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_filter=['fuel_assembly__type','reactor_position','cycle']
    list_display=['cycle','reactor_position','fuel_assembly',]
    list_select_related = ('cycle', 'fuel_assembly')
    raw_id_fields = ("fuel_assembly",)
    ordering=('cycle','reactor_position')
    #list_editable=("fuel_assembly",)
    list_per_page=121
admin.site.register(FuelAssemblyLoadingPattern, FuelAssemblyLoadingPatternAdmin)

class ControlRodAssemblyLoadingPatternInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=ControlRodAssemblyLoadingPattern
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "reactor_position":
            try:
                kwargs["queryset"] = ReactorPosition.objects.filter(reactor_model=Cycle.objects.get(pk=int(request.path.split(sep='/')[-2])).unit.reactor_model)
            except Exception:
                pass
        return super(ControlRodAssemblyLoadingPatternInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class BurnablePoisonAssemblyLoadingPatternInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=BurnablePoisonAssemblyLoadingPattern
    raw_id_fields=('burnable_poison_assembly',)    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print(request.body,request.path,request.POST,request.META)
        if db_field.name == "reactor_position":
            try:
                kwargs["queryset"] = ReactorPosition.objects.filter(reactor_model=Cycle.objects.get(pk=int(request.path.split(sep='/')[-2])).unit.reactor_model)
            except Exception:
                pass
        return super(BurnablePoisonAssemblyLoadingPatternInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class SourceAssemblyLoadingPatternInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=SourceAssemblyLoadingPattern
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "reactor_position":
            try:
                kwargs["queryset"] = ReactorPosition.objects.filter(reactor_model=Cycle.objects.get(pk=int(request.path.split(sep='/')[-2])).unit.reactor_model)
            except Exception:
                pass
        return super(SourceAssemblyLoadingPatternInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
class CycleAdmin(admin.ModelAdmin):
    exclude=('remark',)
    extra=0
    #inlines=[BurnablePoisonAssemblyLoadingPatternInline,ControlRodAssemblyLoadingPatternInline]
    list_display=('pk','__str__','get_pre_cycle','get_cra_cycle')
   
    
    def get_burnable_poison_assembly_num(self,obj):
        num=obj.bpa_loading_patterns.count()
        return num
    get_burnable_poison_assembly_num.short_description='burnable poison assembly count'
    
    def get_source_assembly_num(self,obj):
        num=obj.source_assembly_positions.count()       
        return num
    get_source_assembly_num.short_description='source assembly count'
    
admin.site.register(Cycle, CycleAdmin)


#fuel assembly model information
class GridAdmin(admin.ModelAdmin):
    exclude=('remark',)
    
admin.site.register(Grid, GridAdmin)


class GuideTubeInline(admin.TabularInline):
    exclude=('remark',)
    model=GuideTube

class InstrumentTubeInline(admin.TabularInline):
    exclude=('remark',)
    model=InstrumentTube

    
class GridPositionInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=GridPosition

class UpperNozzleInline(admin.TabularInline):
    exclude=('remark',)
    model=UpperNozzle
    
class LowerNozzleInline(admin.TabularInline):
    exclude=('remark',)
    model=LowerNozzle
    
class FuelElementInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelElement
class FuelPelletInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelPellet
     
class FuelAssemblyModelAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','get_fuel_element_num','get_guide_tube_num','get_instrument_tube_num',)
    inlines=[GridPositionInline,UpperNozzleInline,LowerNozzleInline,GuideTubeInline,InstrumentTubeInline,FuelElementInline,FuelPelletInline]
    
    def get_fuel_element_num(self,obj):
        num=obj.positions.filter(type='fuel').count()
        return num
    get_fuel_element_num.short_description='fuel element count'
    
    def get_guide_tube_num(self,obj):
        num=obj.positions.filter(type='guide').count()
        return num
    get_guide_tube_num.short_description='control rod count'
    
    def get_instrument_tube_num(self,obj):
        num=obj.positions.filter(type='instrument').count()
        return num
    get_instrument_tube_num.short_description='instrument count'
    
admin.site.register(FuelAssemblyModel, FuelAssemblyModelAdmin)

class FuelAssemblyStatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Fuel assembly status')
    # Parameter for the filter that will be used in the URL query.
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status_code'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', _('In core')),
            ('2', _('Spent fuel pool')),
            ('3', _('Fresh')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        query_lst=list(queryset)
      
        if self.value() == '1':
            
            for item in queryset:
                if item.get_fuel_assembly_status()!='In core':
                    query_lst.remove(item)
            return query_lst
        if self.value() == '2':
            for item in queryset:
                if item.get_fuel_assembly_status()!='Spent fuel pool':
                    query_lst.remove(item)
            return queryset
        
        if self.value() == '3':
            for item in queryset:
                if item.get_fuel_assembly_status()!='Fresh':
                    query_lst.remove(item)
            return query_lst


      
#action with parameter
from django.contrib.admin.helpers import ActionForm
from django import forms
class BatchNumberForm(ActionForm):
    batch_number = forms.IntegerField(required=False,label='batch number',min_value=1)
    


class FuelAssemblyRepositoryAdmin(admin.ModelAdmin):
    actions=['update_batch_number','make_disable','make_broken','make_broken_and_disable']
    action_form = BatchNumberForm
    exclude=('remark',)
    list_filter=['type','unit','cycle_positions__cycle','cycle_positions__reactor_position','availability','broken','batch_number',FuelAssemblyStatusListFilter]
    list_display=['pk','type','unit','batch_number',]
    search_fields=('=id',)
    list_select_related = True
    
    #actions
    def update_batch_number(self, request, queryset):
        batch_number = int(request.POST['batch_number'])
        if batch_number<=0:
            self.message_user(request, "you can not input a negative number" ,)
        else:
            queryset.update(batch_number=batch_number)
            self.message_user(request, "Successfully updated batch number for %d rows" % queryset.count(),)
    update_batch_number.short_description = 'Update batch number of selected rows by input batch number besides'

    def make_disable(self, request, queryset):
        if request.user.is_superuser:
            rows_updated=queryset.update(availability=False)
            if rows_updated == 1:
                message_bit = "1 fuel assembly was"
            else:
                message_bit = "%s fuel assemblies were" % rows_updated
            self.message_user(request, "%s successfully marked as disabled." % message_bit)
        else:
            self.message_user(request, "you have no permission")   
    make_disable.short_description='Mark selected fuel assemblies disabled'  
    
    def make_broken(self, request, queryset):
        if request.user.is_superuser:
            rows_updated=queryset.update(broken=True)
            if rows_updated == 1:
                message_bit = "1 fuel assembly was"
            else:
                message_bit = "%s fuel assemblies were" % rows_updated
            self.message_user(request, "%s successfully marked as broken." % message_bit)
        else:
            self.message_user(request, "you have no permission")   
    make_broken.short_description='Mark selected fuel assemblies broken'
    
    def make_broken_and_disable(self, request, queryset):
        if request.user.is_superuser:
            rows_updated=queryset.update(broken=True,availability=False)
            if rows_updated == 1:
                message_bit = "1 fuel assembly was"
            else:
                message_bit = "%s fuel assemblies were" % rows_updated
            self.message_user(request, "%s successfully marked as broken and disable." % message_bit)
        else:
            self.message_user(request, "you have no permission")   
    make_broken_and_disable.short_description='Mark selected fuel assemblies broken and disabled'
admin.site.register(FuelAssemblyRepository, FuelAssemblyRepositoryAdmin)

#fuel assembly type information
class FuelElementTypePositionInline(admin.TabularInline):
    exclude=('remark',)
    
    model=FuelElementTypePosition

class FuelElementTypePositionAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_filter=['fuel_assembly_type','fuel_element_type']
admin.site.register(FuelElementTypePosition, FuelElementTypePositionAdmin)    

    
    
class FuelAssemblyTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('pk','assembly_enrichment','model')
    #list_editable=('assembly_enrichment',)
admin.site.register(FuelAssemblyType, FuelAssemblyTypeAdmin)

class FuelElementPelletLoadingSchemeInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=FuelElementPelletLoadingScheme

class FuelElementTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','get_pellet_composition')
    inlines=[FuelElementPelletLoadingSchemeInline,]
admin.site.register(FuelElementType, FuelElementTypeAdmin)



class FuelPelletTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=['model','material']
admin.site.register(FuelPelletType, FuelPelletTypeAdmin)
#the position information of fuel assembly model

    
class FuelAssemblyPositionAdmin(admin.ModelAdmin):
    list_filter=('fuel_assembly_model','row','column')
    list_display=('__str__','type')
    list_editable=('type',)
    ordering=('row','column')
    exclude=('remark',)
    list_per_page=300 
admin.site.register(FuelAssemblyPosition, FuelAssemblyPositionAdmin)



#fuel element information
class UpperCapInline(admin.TabularInline):
    exclude=('remark',)
    model=UpperCap
    
class LowerCapInline(admin.TabularInline):
    exclude=('remark',)
    model=LowerCap
    
class PlenumSpringInline(admin.TabularInline):
    exclude=('remark',)
    model=PlenumSpring
    
class CladdingTubeInline(admin.TabularInline):
    exclude=('remark',)
    model=CladdingTube

class FuelElementRadialMapInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelElementRadialMap
    
class FuelElementAdmin(admin.ModelAdmin):
    exclude=('remark',) 
    inlines=[FuelElementRadialMapInline,]
admin.site.register(FuelElement, FuelElementAdmin)

#fuel pellet type information    
class FuelPelletAdmin(admin.ModelAdmin):
    exclude=('remark',) 
admin.site.register(FuelPellet, FuelPelletAdmin)

class FakeFuelElementTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
admin.site.register(FakeFuelElementType, FakeFuelElementTypeAdmin)

#########################################################################################
#component assembly rod
class ControlRodRadialMapInline(admin.TabularInline):
    exclude=('remark',)
    model=ControlRodRadialMap

class ControlRodTypeAdmin(admin.ModelAdmin):
    inlines=(ControlRodRadialMapInline,)
    exclude=('remark',)
admin.site.register(ControlRodType, ControlRodTypeAdmin)

class SourceRodTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
admin.site.register(SourceRodType, SourceRodTypeAdmin) 

class NozzlePlugRodAdmin(admin.ModelAdmin):
    exclude=('remark',)
admin.site.register(NozzlePlugRod, NozzlePlugRodAdmin)

class BurnablePoisonMaterialInline(admin.TabularInline):
    model=BurnablePoisonMaterial
    exclude=('remark',) 
    
class BurnablePoisonRodAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[BurnablePoisonMaterialInline,]
admin.site.register(BurnablePoisonRod, BurnablePoisonRodAdmin) 

############################################################################
#burnable poison assembly

class BurnablePoisonRodMapInline(admin.TabularInline):
    exclude=('remark',)
    model=BurnablePoisonRodMap
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "burnable_poison_position":
            try:
                kwargs["queryset"] = FuelAssemblyPosition.objects.filter(fuel_assembly_model=BurnablePoisonAssembly.objects.get(pk=int(request.path.split(sep='/')[-2])).fuel_assembly_model)
            except Exception:
                pass
            
        return super(BurnablePoisonRodMapInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    
    
class BurnablePoisonAssemblyAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[BurnablePoisonRodMapInline]
    list_display=['pk','__str__','get_poison_rod_num','get_quadrant_symbol','get_substitute_bpa']
    
    def get_rod_num(self,obj):
        num=obj.rod_positions.count()
        return num
    get_rod_num.short_description='burnable position rod count'
admin.site.register(BurnablePoisonAssembly, BurnablePoisonAssemblyAdmin)

class BurnablePoisonAssemblyLoadingPatternAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('cycle','reactor_position','burnable_poison_assembly','get_sysmetry_quadrant')
    list_filter=('cycle',)
admin.site.register(BurnablePoisonAssemblyLoadingPattern, BurnablePoisonAssemblyLoadingPatternAdmin)
###############################################################################
#control rod assembly   

class ControlRodMapInline(admin.TabularInline):
    exclude=('remark',)
    model=ControlRodMap

class ControlRodAssemblyAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[ControlRodMapInline,]
    list_display=('__str__','type','cluster',)
admin.site.register(ControlRodAssembly, ControlRodAssemblyAdmin)

class ControlRodAssemblyLoadingPatternAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('reactor_position','control_rod_assembly','cycle',)
    list_filter=('cycle','control_rod_assembly__cluster')
    
admin.site.register(ControlRodAssemblyLoadingPattern, ControlRodAssemblyLoadingPatternAdmin)

class ControlRodClusterAdmin(admin.ModelAdmin):
    exclude=('remark',)
   
    list_display=('__str__','reactor_model','get_control_rod_assembly_num')
admin.site.register(ControlRodCluster, ControlRodClusterAdmin)

##############################################################################
#source assembly 
class SourceRodMapInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=SourceRodMap
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "source_rod_position":
            try:
                kwargs["queryset"] = FuelAssemblyPosition.objects.filter(fuel_assembly_model=SourceAssembly.objects.get(pk=int(request.path.split(sep='/')[-2])).fuel_assembly_model)
                
            except Exception:
                pass
        return super(SourceRodMapInline, self).formfield_for_foreignkey(db_field, request, **kwargs)    
    
class SourceAssemblyAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[SourceRodMapInline,]
admin.site.register(SourceAssembly, SourceAssemblyAdmin)

class SourceAssemblyLoadingPatternAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_filter=('cycle',)
admin.site.register(SourceAssemblyLoadingPattern,SourceAssemblyLoadingPatternAdmin)   

################################################################################ 
#nozzle plug assembly
class NozzlePlugRodMapInline(admin.TabularInline):
    exclude=('remark',)
    model=NozzlePlugRodMap

class NozzlePlugAssemblyAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[NozzlePlugRodMapInline,]
admin.site.register(NozzlePlugAssembly, NozzlePlugAssemblyAdmin)

#####################################################################################
#operation parameter
class ControlRodAssemblyStepInline(admin.TabularInline):
    exclude=('remark',)
    model=ControlRodAssemblyStep

#operation data import 
     
class OperationDailyParameterAdmin(admin.ModelAdmin):

    exclude=('remark',)
    list_display=('cycle','date','burnup','relative_power','critical_boron_density','axial_power_shift',)
    inlines=[ControlRodAssemblyStepInline,]
admin.site.register(OperationDailyParameter, OperationDailyParameterAdmin)

class OperationDistributionDataInline(admin.TabularInline):
    exclude=('remark',)
    model=OperationDistributionData
    
class OperationBankPositionInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=OperationBankPosition

class OperationMonthlyParameterAdmin(admin.ModelAdmin):
    list_display=('cycle','avg_burnup','relative_power','boron_concentration','axial_power_shift','FQ','date',)
    inlines=[OperationBankPositionInline,]
admin.site.register(OperationMonthlyParameter,OperationMonthlyParameterAdmin)

        