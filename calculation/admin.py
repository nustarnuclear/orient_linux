from django.contrib import admin
from .models import *
from .forms import UnitForm,ReactorModelForm,EgretDefaultForm
from .functions import generate_base_core
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from django.template.response import TemplateResponse
# Register your models here.
class PreRobinModelAdmin(admin.ModelAdmin):
    exclude=('remark',)
    
    fieldsets =(
                (None,{
                       'fields':('model_name','default')
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
                       'fields':('reactor_model','max_burnup_point')
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
    )
    list_display=('pk',"__str__",)
admin.site.register(PreRobinBranch, PreRobinBranchAdmin)
 
class AssemblyLaminationInline(admin.TabularInline):
    model=AssemblyLamination
    extra=0
    fields=('height','pre_robin_task',"length","status",'View_task_link')
    readonly_fields=('height','pre_robin_task',"length",'status','View_task_link')
    def has_add_permission(self,request):
        return False
    
    def has_delete_permission(self,request,obj):
        return False
    
    def View_task_link(self, item):
        pk=item.pre_robin_task.pk
        url=reverse("admin:calculation_prerobintask_change",args=[pk])
        return format_html(u'<a href="{url}" target="_blank">View task</a>', url=url)
    View_task_link.short_description = 'View the task'
        
class PreRobinInputAdmin(admin.ModelAdmin):
    add_form_template="no_action.html"
    change_form_template="calculation/auto_cut.html"
    change_list_template="calculation/prerobin_changlist.html"
    exclude=('remark','user')
    inlines=[AssemblyLaminationInline,]
    list_display=('pk','unit','fuel_assembly_type','burnable_poison_assembly','symmetry','cut_already','robin_finished')
    list_filter=("unit",'fuel_assembly_type','burnable_poison_assembly',)
    actions=['auto_cut_selected_inputs']
    def get_urls(self):
        urls = super(PreRobinInputAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/auto_cut/$', self.admin_site.admin_view(self.auto_cut_view),
                name='caculation_prerobininput_auto_cut'),
            
            url(r'^refresh_base_component_link/$', self.admin_site.admin_view(self.refresh_base_component_link_view),
                name='caculation_prerobininput_refresh_base_component_link'),
                          
            url(r'^refresh_base_component/$', self.admin_site.admin_view(self.refresh_base_component_view),
                name='caculation_prerobininput_refresh_base_component'),
            
            url(r'^refresh_loading_pattern_link/$', self.admin_site.admin_view(self.refresh_loading_pattern_link_view),
                name='caculation_prerobininput_refresh_loading_pattern_link'),
                   
            url(r'^refresh_loading_pattern/$', self.admin_site.admin_view(self.refresh_loading_pattern_view),
                name='caculation_prerobininput_refresh_loading_pattern'),
                   
            url(r'^refresh_base_core_link/$', self.admin_site.admin_view(self.refresh_base_core_link_view),
                name='caculation_prerobininput_refresh_base_core_link'),
                   
            url(r'^refresh_base_core/$', self.admin_site.admin_view(self.refresh_base_core_view),
                name='caculation_prerobininput_refresh_base_core'),
            
            url(r'^auto_add_link/$', self.admin_site.admin_view(self.auto_add_link_view),
                name='caculation_prerobininput_auto_add_link'),
            
            url(r'^auto_add/$', self.admin_site.admin_view(self.auto_add_view),
                name='caculation_prerobininput_auto_add'),
            url(r'^auto_cut_all/$', self.admin_site.admin_view(self.auto_cut_all_view),
                name='caculation_prerobininput_auto_cut_all'),
        ]
        return my_urls + urls
    
    def auto_cut_view(self,request, *args, **kwargs):
        try:
            pk=kwargs['pk']
            obj = PreRobinInput.objects.get(pk=pk)
            obj.create_task()
            self.message_user(request, 'Assembly cut completed')
            return redirect(reverse("admin:calculation_prerobininput_change",args=[pk]))
        except:
            self.message_user(request, 'You need to save this input first',messages.WARNING)
            
    
    def auto_cut_all_view(self,request, *args, **kwargs):
        num=0
        for pre_robin_input in PreRobinInput.objects.all(): 
            if not pre_robin_input.cut_already():
                pre_robin_input.create_task()
                num+=1
        self.message_user(request, '%s base fuels(s) auto cut successfully'%num)
        return redirect(reverse("admin:calculation_prerobininput_changelist"))
    
    def auto_cut_selected_inputs(self, request, queryset):
        num=0
        for obj in queryset:
            if not obj.cut_already():
                obj.create_task()
                num+=1
        self.message_user(request, '%s base fuels(s) auto cut successfully'%num)
    #########################################################################################
    def refresh_base_component_link_view(self,request, *args, **kwargs):
        context={"reactor_model_form":ReactorModelForm}
        return TemplateResponse(request, "calculation/refresh_base_component.html", context)
       
    def refresh_base_component_view(self,request, *args, **kwargs):
        if request.method == 'POST':
            form = ReactorModelForm(request.POST)
            if form.is_valid():
                reactor_model=form.cleaned_data['reactor_model']
                PreRobinInput.write_base_component_xml(reactor_model)
                self.message_user(request, 'Refresh succeed')
                return redirect(reverse("admin:calculation_prerobininput_changelist"))
    ##########################################################################################
    def refresh_loading_pattern_link_view(self,request, *args, **kwargs):
        context={"unit_form":UnitForm}
        return TemplateResponse(request, "calculation/refresh_loading_pattern.html", context)
    
    def refresh_loading_pattern_view(self,request, *args, **kwargs):
        if request.method == 'POST':
            form = UnitForm(request.POST)
            if form.is_valid():
                unit=form.cleaned_data['unit']
                PreRobinInput.write_loading_pattern_xml(unit)
                self.message_user(request, 'Refresh succeed')
                return redirect(reverse("admin:calculation_prerobininput_changelist"))
    ##########################################################################################      
    def refresh_base_core_link_view(self,request, *args, **kwargs):
        context={"egret_default_form":EgretDefaultForm().as_p()}
        return TemplateResponse(request, "calculation/refresh_base_core.html", context)
    
    def refresh_base_core_view(self,request, *args, **kwargs):
        if request.method == 'POST':
            form = EgretDefaultForm(request.POST)
            if form.is_valid():
                unit=form.cleaned_data['unit']
                calc_data={}
                calc_data['subdivision']=form.cleaned_data['subdivision']
                calc_data['num_radial_brs']=form.cleaned_data['num_radial_brs']
                calc_data['bot_br_size']=str(form.cleaned_data['bot_br_size'])
                calc_data['top_br_size']=str(form.cleaned_data['top_br_size'])
                calc_data['fold_core']=form.cleaned_data['fold_core']
                calc_data['axial_df']=form.cleaned_data['axial_df']
                calc_data['axial_mesh']=str(form.cleaned_data['axial_mesh'])
                calc_data['cyclen_std_bu']=form.cleaned_data['cyclen_std_bu']
                generate_base_core(unit,calc_data)
                self.message_user(request, 'Refresh succeed')
                return redirect(reverse("admin:calculation_prerobininput_changelist"))
    
    def auto_add_link_view(self,request, *args, **kwargs):
        context={"unit_form":UnitForm}
        return TemplateResponse(request, "calculation/auto_add_pre_robin.html", context)
    
    
    def auto_add_view(self,request, *args, **kwargs):
        if request.method == 'POST':
            form = UnitForm(request.POST)
            if form.is_valid():
                unit=form.cleaned_data['unit']
                num=PreRobinInput.auto_add(unit)
                
            self.message_user(request, '{} base fuel(s) concerning {} have been added into database'.format(num, unit))
        else:
            self.message_user(request, 'You have no such permission',messages.WARNING)
        return redirect(reverse("admin:calculation_prerobininput_changelist"))
    
admin.site.register(PreRobinInput, PreRobinInputAdmin)   

class DepletionStateAdmin(admin.ModelAdmin):
    list_display=['__str__','get_task_num']
admin.site.register(DepletionState, DepletionStateAdmin)

class RobinTaskInline(admin.TabularInline):
    model=RobinTask
    extra=0
    fields = ('name', 'input_file','server', 'task_status','start_time','end_time','logfile_link','outfile_link')
    readonly_fields=('name','pre_robin_task','input_file','start_time','end_time','logfile_link','outfile_link')
    #readonly_fields=('logfile_link','outfile_link')
    list_editable=('task_status',)
    def has_add_permission(self,request):
        return False
    
    def has_delete_permission(self,request,obj):
        return False
    
    def logfile_link(self, item):
        url = item.get_logfile_url()
        return format_html(u'<a href="{url}">Get log file</a>', url=url)
    logfile_link.short_description = 'Get log file'
    
    def outfile_link(self, item):
        url = item.get_outfile_url()
        return format_html(u'<a href="{url}">Get out file</a>', url=url)
    outfile_link.short_description = 'Get out file'
    
class PreRobinTaskAdmin(admin.ModelAdmin):
    add_form_template="no_action.html"
    change_form_template="calculation/change_form_template.html"
    list_display=("__str__","plant",'fuel_assembly_type','branch','depletion_state','pre_robin_model','task_status','robin_finished','table_generated','bp_in',)
    exclude=('remark','user')
    inlines=[RobinTaskInline,]
    readonly_fields=('plant','fuel_assembly_type','pin_map','fuel_map',)
    actions = ['auto_start_prerobin','del_all_robin_tasks','auto_start_robin','auto_start_idyll']
    list_filter=("plant","task_status")
    def auto_start_prerobin(self, request, queryset):
        index=0
        for obj in queryset.exclude(task_status=4):
            return_code=obj.start_prerobin()
            if return_code!=0:
                index +=1
        self.message_user(request, 'All selected tasks have been handled with %d error(s) left'%index)
        
    def del_all_robin_tasks(self, request, queryset):
        for obj in queryset:
            robin_tasks=obj.robin_tasks.all()
            if not robin_tasks.filter(task_status=1).exists():
                robin_tasks.delete()
        self.message_user(request, 'all robin tasks are deleted')
        
    def auto_start_robin(self,request, queryset):
        for obj in queryset:
            obj.start_robin()
        self.message_user(request, '%d robin tasks are under calculation'%(queryset.count()*13))
        
    def auto_start_idyll(self,request,queryset):
        index=0
        for obj in queryset:
            if obj.robin_finished:  
                index +=1
                obj.start_all_idyll()
        left=queryset.count()-index
        self.message_user(request, '{} idyll tasks completed while {} idyll tasks left'.format(index,left))      
            
    def get_urls(self):
        urls = super(PreRobinTaskAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/start_prerobin/$', self.admin_site.admin_view(self.start_prerobin_view),
                name='caculation_prerobininput_start_prerobin'),
                   
            url(r'^(?P<pk>\d+)/start_robin/$', self.admin_site.admin_view(self.start_robin_view),
                name='caculation_prerobininput_start_robin'),
            
            url(r'^(?P<pk>\d+)/stop_robin/$', self.admin_site.admin_view(self.stop_robin_view),
                name='caculation_prerobininput_stop_robin'),
            
            url(r'^(?P<pk>\d+)/delete_robin/$', self.admin_site.admin_view(self.delete_robin_view),
                name='caculation_prerobininput_delete_robin'),
            
            url(r'^(?P<pk>\d+)/start_idyll/$', self.admin_site.admin_view(self.start_idyll_view),
                name='caculation_prerobininput_start_idyll'),
        ]
        return my_urls + urls
    
    def start_prerobin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = PreRobinTask.objects.get(pk=pk)
        if obj.robin_tasks.exists():
            self.message_user(request, 'Robin tasks already exist, you need to delete all robin tasks if you want to recalculate',messages.WARNING)
        else:
            return_code=obj.start_prerobin()
            #PreROBIN went wrong
            if return_code!=0:
                self.message_user(request, 'PreROBIN failed',messages.ERROR)
            else:
                self.message_user(request, 'Calculation completed',)
            obj.save()
        return redirect(reverse("admin:calculation_prerobintask_change",args=[pk]))
    
    def start_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = PreRobinTask.objects.get(pk=pk)
        obj.start_robin()
        self.message_user(request, 'all robin tasks are under calculation')
        return redirect(reverse("admin:calculation_prerobintask_change",args=[pk]))
    
    def stop_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = PreRobinTask.objects.get(pk=pk)
        obj.stop_robin()
        self.message_user(request, 'all robin tasks have been stopped')
        return redirect(reverse("admin:calculation_prerobintask_change",args=[pk]))
    
    def delete_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = PreRobinTask.objects.get(pk=pk)
        robin_tasks=obj.robin_tasks.all()
        if robin_tasks.filter(task_status=1).exists():
            self.message_user(request, 'You need to stop ROBIN first',messages.WARNING)
        else:
            robin_tasks.delete()
            #delete prerobin files
            cwd=obj.get_cwd()
            task_name=os.path.basename(cwd)
            os.chdir(os.path.dirname(cwd))
            shutil.rmtree(task_name)
            self.message_user(request, 'all robin tasks have been deleted')
        return redirect(reverse("admin:calculation_prerobintask_change",args=[pk]))
    
    def start_idyll_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = PreRobinTask.objects.get(pk=pk)
        if not obj.robin_finished:  
            self.message_user(request, 'Your need to wait all robin tasks finished',messages.WARNING)
        else:
            obj.start_all_idyll()
            self.message_user(request, 'table generated completed')
        return redirect(reverse("admin:calculation_prerobintask_change",args=[pk]))
    
admin.site.register(PreRobinTask, PreRobinTaskAdmin)

class RobinTaskAdmin(admin.ModelAdmin):
    list_display=('pk','__str__',"logfile_link","outfile_link","get_burnup","base",'get_base')
    exclude=('core_baffle_calc',)
    def logfile_link(self, item):
        url = item.get_logfile_url()
        return format_html(u'<a href="{url}">Get log file</a>', url=url)
    logfile_link.short_description = 'Get log file'
    
    def outfile_link(self, item):
        url = item.get_outfile_url()
        return format_html(u'<a href="{url}">Get out file</a>', url=url)
    logfile_link.short_description = 'Get out file'
    
admin.site.register(RobinTask, RobinTaskAdmin)


class CoreBaffleCalculationAdmin(admin.ModelAdmin):
    add_form_template="no_action.html"
    change_form_template="calculation/change_form_template.html"
    list_display=('__str__','get_idyll_inputs')
    inlines=[RobinTaskInline]
    def get_urls(self):
        urls = super(CoreBaffleCalculationAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/start_prerobin/$', self.admin_site.admin_view(self.start_prerobin_view),
                name='caculation_corebafflecalculation_start_prerobin'),
                   
            url(r'^(?P<pk>\d+)/start_robin/$', self.admin_site.admin_view(self.start_robin_view),
                name='caculation_corebafflecalculation_start_robin'),
            
#             url(r'^(?P<pk>\d+)/stop_robin/$', self.admin_site.admin_view(self.stop_robin_view),
#                 name='caculation_corebafflecalculation_stop_robin'),
#                 
            url(r'^(?P<pk>\d+)/delete_robin/$', self.admin_site.admin_view(self.delete_robin_view),
                name='caculation_corebafflecalculation_delete_robin'),
            
            url(r'^(?P<pk>\d+)/start_idyll/$', self.admin_site.admin_view(self.start_idyll_view),
                name='caculation_corebafflecalculation_start_idyll'),
        ]
        return my_urls + urls
    
    def start_prerobin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = CoreBaffleCalculation.objects.get(pk=pk)
        if obj.robin_tasks.exists():
            self.message_user(request, 'Robin tasks already exist, you need to delete all robin tasks if you want to recalculate',messages.WARNING)
        else:
            return_code=obj.create_all_tasks()
            #PreROBIN went wrong
            if return_code!=0:
                self.message_user(request, 'PreROBIN failed',messages.ERROR)
            else:
                self.message_user(request, 'Calculation completed',)
            obj.save()
        return redirect(reverse("admin:calculation_corebafflecalculation_change",args=[pk]))
    
    def start_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = CoreBaffleCalculation.objects.get(pk=pk)
        obj.start_robin()
        self.message_user(request, 'all robin tasks are under calculation')
        return redirect(reverse("admin:calculation_corebafflecalculation_change",args=[pk]))
    
    def stop_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = CoreBaffleCalculation.objects.get(pk=pk)
        obj.stop_robin()
        self.message_user(request, 'all robin tasks have been stopped')
        return redirect(reverse("admin:calculation_corebafflecalculation_change",args=[pk]))
    
    def delete_robin_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = CoreBaffleCalculation.objects.get(pk=pk)
        robin_tasks=obj.robin_tasks.all()
        if robin_tasks.filter(task_status=1).exists():
            self.message_user(request, 'You need to stop ROBIN first',messages.WARNING)
        else:
            robin_tasks.delete()
            #delete prerobin files
            for model_type in CoreBaffleCalculation.MODEL_TYPES:
                cwd=obj.get_cwd(model_type)
                task_name=os.path.basename(cwd)
                os.chdir(os.path.dirname(cwd))
                shutil.rmtree(task_name)
            self.message_user(request, 'all robin tasks have been deleted')
        return redirect(reverse("admin:calculation_corebafflecalculation_change",args=[pk]))
    
    def start_idyll_view(self,request, *args, **kwargs):
        pk=kwargs['pk']
        obj = CoreBaffleCalculation.objects.get(pk=pk)
        if not obj.robin_finished:  
            self.message_user(request, 'Your need to wait all robin tasks finished',messages.WARNING)
        else:
            return_codes=obj.start_all_idyll()
            self.message_user(request, 'table generated completed,return code set is %s'%return_codes)
        return redirect(reverse("admin:calculation_corebafflecalculation_change",args=[pk]))
admin.site.register(CoreBaffleCalculation, CoreBaffleCalculationAdmin)

class EgretTaskAdmin(admin.ModelAdmin):  
    exclude=('remark',)
    list_display=('pk','user','task_name','task_type','start_time','end_time','time_cost','task_status','remark','recalculated','locked','get_base_dir')
    list_filter=('loading_pattern__cycle','loading_pattern__cycle__unit','loading_pattern__cycle__unit__plant')
    
    def get_queryset(self, request):
        qs = super(EgretTaskAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
admin.site.register(EgretTask, EgretTaskAdmin)

class ServerAdmin(admin.ModelAdmin):
    list_display=("name","IP","queue",'next')
    #inlines=[RobinTaskInline,]
admin.site.register(Server,ServerAdmin)

class MultipleLoadingPatternAdmin(admin.ModelAdmin): 
    exclude=('remark',) 
    list_display=('pk','name','authorized','visibility',)
    list_filter=('cycle',)
    def get_queryset(self, request):
        qs = super(MultipleLoadingPatternAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
admin.site.register(MultipleLoadingPattern, MultipleLoadingPatternAdmin)      

