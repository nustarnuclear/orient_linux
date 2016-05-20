from django.contrib import admin
from .models import *
from django.db.models import F,Count
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
# Register your models here.

#################################################
#basic information 
#################################################
def get_obj(request,model):
    path=request.path
    pk=path.split('/')[-2]
    return model.objects.get(pk=int(pk))
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
    list_filter=('element','id_wims','nf','material_type',)
    search_fields=('=id_wims','=element__symbol','=id_self_defined')
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
    search_fields=('element_name',)
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



class MaterialWeightCompositionInline(admin.TabularInline):
    model=MaterialWeightComposition
    exclude=('remark',)
    extra=0

class MaterialVolumeCompositionInline(admin.TabularInline):
    model=MaterialVolumeComposition
    exclude=('remark',)
    extra=0
    fk_name='mixture'
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
    inlines=(MaterialWeightCompositionInline,MaterialVolumeCompositionInline)
    exclude=('remark',)
    
    list_display=('pk','__str__','is_correct',)
    
    def get_readonly_fields(self,request, obj=None):
        if not request.user.is_superuser:
            return ('nameEN','nameCH')
        return ()
    
    #check if satisfy the integrity constraint
    def is_correct(self,obj):
        pecentage_sum=obj.weight_mixtures.all().aggregate(sum=Sum('percent'))
        if pecentage_sum['sum']:
            if abs(pecentage_sum['sum']-100)<=0.1:return True
            else:return False
        else:
            return True
    is_correct.short_description='Data Integrity?'
    is_correct.boolean=True       
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
    list_display=('reactor_model','__str__','control_rod_cluster','get_quadrant_symbol','in_outermost')
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
    inlines=[CoreBaffleInline,CoreUpperPlateInline,CoreLowerPlateInline,ThermalShieldInline,PressureVesselInline,PressureVesselInsulationInline,CoreBaffleInline,]
    list_display=['pk','name','generation','reactor_type','get_thermal_couple_num','get_incore_instrument_num','get_fuel_assembly_num','dimension','middle','start_pos','end_pos','quarter_pos','generate_reflector_line','generate_reflector_index']
    
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
    list_display=('__str__','get_current_cycle','base_core_path',)
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
    list_filter=['fuel_assembly__type','reactor_position','cycle',]
    list_display=['cycle','reactor_position','fuel_assembly','burnable_poison_assembly','cr_out']
    list_select_related = ('cycle', 'fuel_assembly')
    raw_id_fields = ("fuel_assembly",)
    ordering=('cycle','reactor_position')
    #list_editable=("cr_out",)
    list_per_page=157
admin.site.register(FuelAssemblyLoadingPattern, FuelAssemblyLoadingPatternAdmin)
    
class CycleAdmin(admin.ModelAdmin):
    exclude=('remark',)
    extra=0
    list_display=('pk','__str__',)
    add_form_template="no_action.html"
    change_form_template="tragopan/refresh_loading_pattern.html"
    actions = ['refresh_loading_pattern']
    def get_urls(self):
        urls = super(CycleAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/refresh_loading_pattern/$', self.admin_site.admin_view(self.refresh_loading_pattern_view),
                name='tragopan_cycle_refresh_loading_pattern'),
        ]
        return my_urls + urls
    
    def refresh_loading_pattern_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj=Cycle.objects.get(pk=pk)
        obj.refresh_loading_pattern()
        self.message_user(request, 'Loading pattern xml file has been refreshed successfully')
        return redirect(reverse("admin:tragopan_cycle_change",args=[pk]))
    
    def refresh_loading_pattern(self, request, queryset):
        for obj in queryset:
            obj.refresh_loading_pattern()
        self.message_user(request, 'All loading pattern xml files have been refreshed successfully')    
admin.site.register(Cycle, CycleAdmin)


#fuel assembly model information
class GridAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','grid_volume','water_volume','type_num')
    list_filter=('fuel_assembly_model',)
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
#     def formfield_for_foreignkey(self, db_field,request, **kwargs):
#         if db_field.name=='grid':
#             obj=self.get_obj(request,FuelAssemblyModel)
#             kwargs["queryset"] = Grid.objects.filter(fuel_assembly_model=obj)
#         return super(GridPositionInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class UpperNozzleInline(admin.TabularInline):
    exclude=('remark',)
    model=UpperNozzle
    
class LowerNozzleInline(admin.TabularInline):
    exclude=('remark',)
    model=LowerNozzle
    
class FuelElementInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelElement
    extra=0
class FuelPelletInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelPellet
    
class FuelAssemblyPositionInline(admin.TabularInline):
    exclude=('remark',)
    model=FuelAssemblyPosition
    extra=0
    
class FuelAssemblyModelAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','get_fuel_element_num','get_wet_frac',)
    inlines=[GridPositionInline,GuideTubeInline,InstrumentTubeInline,FuelElementInline,FuelPelletInline,FuelAssemblyPositionInline]
    add_form_template="no_action.html"
    change_form_template="tragopan/distribute_tube.html"
    def get_urls(self):
        urls = super(FuelAssemblyModelAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/distribute_tube/$', self.admin_site.admin_view(self.distribute_tube_view),
                name='tragopan_fuel_assembly_model_distribute_tube'),
        ]
        return my_urls + urls
    
    def distribute_tube_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj=FuelAssemblyModel.objects.get(pk=pk)
        num=obj.distribute_tube()
        self.message_user(request, '%d tube positions have been set successfully'%num)
        return redirect(reverse("admin:tragopan_fuelassemblymodel_change",args=[pk]))
    
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
    list_filter=['type','unit','cycle_positions__cycle','cycle_positions__reactor_position','availability','broken','batch_number',]
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
    raw_id_fields=("fuel_assembly_position","fuel_element_type")
    extra=0
    def has_delete_permission(self,request,obj):
        return False
    
    def has_add_permission(self,request):
        return False

class FuelElementTypePositionAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_filter=['fuel_assembly_type','fuel_element_type']
admin.site.register(FuelElementTypePosition, FuelElementTypePositionAdmin)    

 
    
class FuelAssemblyTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('pk','assembly_enrichment','model',)
    inlines=[FuelElementTypePositionInline]
    add_form_template="no_action.html"
    change_form_template="tragopan/insert_fuel.html"
    def get_urls(self):
        urls = super(FuelAssemblyTypeAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/insert_fuel/$', self.admin_site.admin_view(self.insert_fuel_view),
                name='tragopan_fuel_assembly_type_insert_fuel'),
        ]
        return my_urls + urls
    
    def insert_fuel_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj=FuelAssemblyType.objects.get(pk=pk)
        num=obj.insert_fuel()
        self.message_user(request, '%d fuel elements have been inserted successfully'%num)
        return redirect(reverse("admin:tragopan_fuelassemblytype_change",args=[pk]))
     
admin.site.register(FuelAssemblyType, FuelAssemblyTypeAdmin)

class FuelElementPelletLoadingSchemeInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=FuelElementPelletLoadingScheme
    def formfield_for_foreignkey(self, db_field,request, **kwargs):
        if db_field.name=='fuel_pellet_type':
            obj=get_obj(request,FuelElementType)
            kwargs["queryset"] = FuelPelletType.objects.filter(model__fuel_assembly_model=obj.model.fuel_assembly_model)
            return super(FuelElementPelletLoadingSchemeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
class FuelElementTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','enrichment')
    inlines=[FuelElementPelletLoadingSchemeInline,]
admin.site.register(FuelElementType, FuelElementTypeAdmin)



class FuelPelletTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=['model','material','enrichment',]
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

class FuelElementSectionInline(admin.TabularInline):
    model=FuelElementSection
    extra=0
    exclude=('remark',)
    
class FuelElementAdmin(admin.ModelAdmin):
    exclude=('remark',) 
    inlines=[CladdingTubeInline,FuelElementSectionInline]
admin.site.register(FuelElement, FuelElementAdmin)

class TransectionMaterialInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    model=TransectionMaterial
    
class MaterialTransectionAdmin(admin.ModelAdmin):
    inlines=[TransectionMaterialInline,]
    list_display=('pk',"__str__","if_fuel",'if_control_rod','if_bp_rod','material_set','radius')
admin.site.register(MaterialTransection, MaterialTransectionAdmin)

#fuel pellet type information    
class FuelPelletAdmin(admin.ModelAdmin):
    exclude=('remark',) 
    list_display=('fuel_assembly_model','factor')
admin.site.register(FuelPellet, FuelPelletAdmin)
#########################################################################################
#component assembly rod
    
class ControlRodSectionInline(admin.TabularInline):
    exclude=('remark',)
    model=ControlRodSection

class ControlRodTypeAdmin(admin.ModelAdmin):
    inlines=(ControlRodSectionInline,)
    list_display=('pk','__str__','height_lst','generate_material_transection_set')
    exclude=('remark',)
admin.site.register(ControlRodType, ControlRodTypeAdmin)



 

class BurnablePoisonSectionInline(admin.TabularInline):
    model=BurnablePoisonSection
    exclude=('remark',)
    extra=0
    
class BurnablePoisonRodAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('pk','__str__','height_lst','max_section_num')
    inlines=(BurnablePoisonSectionInline,)
admin.site.register(BurnablePoisonRod, BurnablePoisonRodAdmin) 

############################################################################
#burnable poison assembly
class BurnablePoisonAssemblyMapAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=['pk','__str__',"row","column","reflect_4th_quandrant","generate_quadrant_symbol"]
admin.site.register(BurnablePoisonAssemblyMap, BurnablePoisonAssemblyMapAdmin)

class BurnablePoisonAssemblyMapInline(admin.TabularInline):
    exclude=('remark',)
    model=BurnablePoisonAssemblyMap
    
    
class BurnablePoisonAssemblyAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[BurnablePoisonAssemblyMapInline,]
    list_display=['pk','__str__','get_poison_rod_num','get_quadrant_symbol','height_lst','symmetry','get_symmetry_bpa']
    def get_rod_num(self,obj):
        num=obj.rod_positions.count()
        return num
    get_rod_num.short_description='burnable position rod count'
admin.site.register(BurnablePoisonAssembly, BurnablePoisonAssemblyAdmin)

#control rod assembly   
class ControlRodAssemblyMapInline(admin.TabularInline):
    model=ControlRodAssemblyMap
    exclude=('remark',)

class ControlRodAssemblyTypeAdmin(admin.ModelAdmin):
    exclude=('remark',)
    inlines=[ControlRodAssemblyMapInline,]
    model=ControlRodAssemblyType
    list_display=('pk','reactor_model','black_grey_rod_num','height_lst','start_index','end_index','length_lst','type_lst','get_branch_ID_set')
admin.site.register(ControlRodAssemblyType, ControlRodAssemblyTypeAdmin)
   
class ControlRodClusterAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('pk','__str__','control_rod_assembly_type',)
    list_filter=('control_rod_assembly_type__reactor_model',)
admin.site.register(ControlRodCluster, ControlRodClusterAdmin)


#####################################################################################
#operation parameter
class ControlRodAssemblyStepInline(admin.TabularInline):
    exclude=('remark',)
    model=ControlRodAssemblyStep

#operation data import 
     
class OperationDailyParameterAdmin(admin.ModelAdmin):

    exclude=('remark',)
    list_display=('cycle','date','burnup','relative_power','critical_boron_density',)
    inlines=[ControlRodAssemblyStepInline,]
admin.site.register(OperationDailyParameter, OperationDailyParameterAdmin)

class OperationDistributionDataInline(admin.TabularInline):
    exclude=('remark',)
    raw_id_fields=('reactor_position',)
    model=OperationDistributionData
    extra=0
    readonly_fields=('reactor_position','relative_power','FDH',)
    def has_add_permission(self,request):
        return False
    def has_delete_permission(self,request, obj=None):
        return False
class OperationBankPositionInline(admin.TabularInline):
    exclude=('remark',)
    extra=0
    raw_id_fields=('control_rod_cluster',)
    model=OperationBankPosition
    readonly_fields=('control_rod_cluster','step')
    def has_add_permission(self,request):
        return False
    def has_delete_permission(self,request, obj=None):
        return False
    
class OperationMonthlyParameterAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('cycle','avg_burnup','relative_power','boron_concentration','axial_power_offset','FQ','date',)
    inlines=[OperationBankPositionInline,OperationDistributionDataInline]
    readonly_fields=('date','avg_burnup','relative_power','boron_concentration','axial_power_offset','FQ',)
admin.site.register(OperationMonthlyParameter,OperationMonthlyParameterAdmin)

        