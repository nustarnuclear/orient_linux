from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.

class PreRobinModelAdmin(admin.ModelAdmin):
    exclude=('remark',)
    
    fieldsets =(
                (None,{
                       'fields':('model_name','user','system_pressure',)
                }),
                
                ('accuracy control',{
                                     'classes': ('grp-collapse grp-closed',),
                                     'fields':('track_density','polar_type','polar_azimuth','iter_inner','iter_outer','eps_keff','eps_flux')
                }),
                ('fundamental mode',{
                                     'classes': ('grp-collapse grp-closed',),
                                     'fields':('leakage_corrector_path','leakage_corrector_method','buckling_or_keff',)
                }),
                ('energy condensation',{
                                        'classes': ('grp-collapse grp-closed',),
                                        'fields':('condensation_path','num_group_2D',)
                                     
                }),
                ('edit control',{
                                 'classes': ('grp-collapse grp-closed',),
                                 'fields':('num_group_edit','micro_xs_output',)
                                     
                }),
    )
    
    class Media:
        js = [
              '/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/tinymce_setup.js',
        ]
admin.site.register(PreRobinModel, PreRobinModelAdmin)


class PreRobinBranchAdmin(admin.ModelAdmin):
    fieldsets =(
                (None,{
                       'fields':('unit','max_burnup_point')
                }),
                
                ('boron density branch',{
                                     'classes': ('grp-collapse grp-closed',),
                                     'fields':('max_boron_density','min_boron_density','boron_density_interval',)
                }),
                ('fuel temperature branch',{
                                     'classes': ('grp-collapse grp-closed',),
                                     'fields':('max_fuel_temperature','min_fuel_temperature','fuel_temperature_interval',)
                }),
                ('moderator temperature branch',{
                                        'classes': ('grp-collapse grp-closed',),
                                        'fields':('max_moderator_temperature','min_moderator_temperature','moderator_temperature_interval')
                                     
                }),
                ('shutdown cooling branch',{
                                 'classes': ('grp-collapse grp-closed',),
                                 'fields':('shutdown_cooling_days',)
                                     
                }),
                ('xenon branch',{
                                 'classes': ('grp-collapse grp-closed',),
                                 'fields':('xenon',)
                                     
                }),
    )
admin.site.register(PreRobinBranch, PreRobinBranchAdmin)
    
class PreRobinInputAdmin(admin.ModelAdmin):
    exclude=('remark','user')
    list_display=('pk','unit','fuel_assembly_type','burnable_poison_assembly','symmetry','auto_generate_transection')
admin.site.register(PreRobinInput, PreRobinInputAdmin)   

class IbisAdmin(admin.ModelAdmin):
    exclude=('remark','user')
    list_display=('__str__','plant','burnable_poison_assembly','ibis_path')
    list_editable=('burnable_poison_assembly',)
    list_filter=('plant',)
admin.site.register(Ibis, IbisAdmin)    

class RobinFileAdmin(admin.ModelAdmin):
    exclude=('remark',)
    list_display=('__str__','input_file','out1_file','log_file')
admin.site.register(RobinFile, RobinFileAdmin)     

class BaseFuelCompositionInline(admin.TabularInline):
    model=BaseFuelComposition
    exclude=('remark',)


class BaseFuelAdmin(admin.ModelAdmin):
    exclude=('remark','user')
    inlines=(BaseFuelCompositionInline,)
    list_display=('__str__','get_ibis_composition','composition_set','if_insert_burnable_fuel','offset',)
    list_filter=('plant',)
    list_editable=('offset',)
    def get_ibis_composition(self,obj):
        ibis_composition=obj.composition.all()
        result=''
        for ibis in ibis_composition:
            result = result+' '+ibis.ibis.ibis_name
        return  result
    get_ibis_composition.short_description='ibis file name'
    
admin.site.register(BaseFuel, BaseFuelAdmin) 
    

class EgretTaskAdmin(admin.ModelAdmin):  
    exclude=('remark',)
    list_display=('pk','user','task_name','task_type','start_time','end_time','time_cost','task_status','remark','if_recalculated','locked')
    list_filter=('loading_pattern__cycle','loading_pattern__cycle__unit','loading_pattern__cycle__unit__plant')
    
    def start_calculation_link(self,obj):
        #dest = reverse('admin:calculation_pictures_mail_author', kwargs={'pk': obj.pk})
        dest='http://www.baidu.com'
        #use get_urls()
        return format_html('<a href="{url}">{title}</a>',
                           url=dest, title='send mail')
    start_calculation_link.short_description = 'Start calculation'
    start_calculation_link.allow_tags = True
    
    
    def get_queryset(self, request):
        qs = super(EgretTaskAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
admin.site.register(EgretTask, EgretTaskAdmin)



class MultipleLoadingPatternAdmin(admin.ModelAdmin): 
    exclude=('remark',) 
    list_display=('pk','name','authorized','visibility')
    list_filter=('cycle',)
    def get_queryset(self, request):
        qs = super(MultipleLoadingPatternAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
admin.site.register(MultipleLoadingPattern, MultipleLoadingPatternAdmin)      

