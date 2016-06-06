from django.conf.urls import url
from tragopan import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
    url(r'^plant/$', views.PlantViewSet.as_view({'get': 'list'})),
    url(r'^fuel_assembly_detail/$', views.fuel_assembly_detail),
    url(r'^operation_data/$',views.operation_data),
    url(r'^fuel_assembly_model/(?P<pk>[0-9]+)/$',views.FuelAssemblyModelViewSet.as_view({'get': 'retrieve'})),
    url(r'^cycle/(?P<pk>[0-9]+)/$',views.CycleViewSet.as_view({'get': 'retrieve'})),
    url(r'^cycle/$',views.CycleViewSet.as_view({'get': 'list'})),
    url(r'^create_cycle/$',views.CycleViewSet.as_view({'post': 'create'})),
    url(r'^abnormal_fuel_assembly/$',views.AbnormalFuelAssembly.as_view({'get': 'list'})),
]

urlpatterns = format_suffix_patterns(urlpatterns)