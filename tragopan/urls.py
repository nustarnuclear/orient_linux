from django.conf.urls import url
from tragopan import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
    #url(r'^fuel_assembly_loading_pattern/$', views.fuel_assembly_loading_pattern_list),
    #url(r'^fuel_assembly_loading_patterns/(?P<pk>[0-9]+)/$', views.fuel_assembly_loading_pattern_detail),
    #url(r'^(?P<plantname>.+?)/unit(?P<unit_num>[1-4])/cycle(?P<cycle_num>[0-9]+)/$', views.cycle_detail),
    url(r'^plant_list/$', views.plant_list),
    url(r'^fuel_assembly_type/$', views.fuel_assembly_type_list),
    url(r'^fuel_assembly_detail/$', views.fuel_assembly_detail),
    url(r'^operation_data/$',views.operation_data),
]

urlpatterns = format_suffix_patterns(urlpatterns)