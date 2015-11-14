from django.conf.urls import url
from calculation import views
urlpatterns = [
    url(r'^egret_task/$',views.egret_task),
    url(r'^multiple_loading_pattern/$',views.multiple_loading_pattern),
    url(r'^upload_loading_pattern/$',views.upload_loading_pattern),
]