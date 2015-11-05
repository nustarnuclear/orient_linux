from django.conf.urls import url
from calculation import views
urlpatterns = [
    url(r'^egret_task/$',views.generate_egret_task),
    url(r'^multiple_loading_pattern/(?P<plantname>.+?)/unit(?P<unit_num>[1-4])/cycle(?P<cycle_num>[0-9]+)/$',views.generate_loading_pattern),
    url(r'^upload_loading_pattern/(?P<plantname>.+?)/unit(?P<unit_num>[1-4])/cycle(?P<cycle_num>[0-9]+)/$',views.upload_loading_pattern),
]