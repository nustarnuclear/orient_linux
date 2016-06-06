from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()
from django.conf import settings
from filebrowser.sites import site
from django.conf.urls.static import static
from django.contrib.auth.models import User,Group
from rest_framework import permissions, routers, serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken import views as authtokenviews
from . import views
from django.views.generic import RedirectView

# first we define the serializers
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class GroupViewSet(viewsets.ModelViewSet):
    #permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    #required_scopes = ['groups']
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.



urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^favicon.ico$', RedirectView.as_view(url='/static/admin/img/favicon.ico', permanent=True)),    
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tragopan/', include('tragopan.urls',namespace="tragopan")),
    url(r'^calculation/', include('calculation.urls',namespace="calculation")),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', authtokenviews.obtain_auth_token),
    url(r'^change_password/', views.change_password),
    url(r'^admin_log/',views.LogEntryViewSet.as_view({'get': 'list'})),
      
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

