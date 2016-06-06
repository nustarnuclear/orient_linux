"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'tragopan.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        
        self.children.append(modules.Group(
            _('ASSEMBLY CALCULATION'),
            column=1,
            collapsible=True,
            children = [
                modules.ModelList(
#                     _('ROBIN'),
                    css_classes=('grp-background-color grp-yellow',),
                    models=('calculation.models.PreRobinInput','calculation.models.PreRobinTask','calculation.models.CoreBaffleCalculation'),
                ),
#                 modules.ModelList(
#                     _('EGRET'),
#                     css_classes=('grp-collapse grp-closed',),
#                     models=('calculation.models.*Egret*','calculation.models.MultipleLoadingPattern',),
#                 ),
                         
            ]
        ))
        
#         # append a group for "Administration" & "Applications"
#         self.children.append(modules.Group(
#             _('Group: Administration'),
#             column=2,
#             collapsible=True,
#             children = [
#                 modules.AppList(
#                     _('Administration'),
#                     collapsible=True,
#                     models=('django.contrib.*',),
#                 ),
# #                 modules.AppList(
# #                     _('Applications'),
# #                     css_classes=('collapse closed',),
# #                     exclude=('django.contrib.*','rest_framework.authtoken.*',),
# #                 ),
#             ]
#         ))

        self.children.append(modules.Group(
            _('FUEL ASSEMBLY MODELING'),
            column=1,
            collapsible=True,
            css_classes=('grp-collapse grp-closed',),
            children = [
                modules.ModelList(
                                  title='MATERIAL',
                                  column=1,
                                  models=('tragopan.models.BasicMaterial','tragopan.models.Material','tragopan.models.MaterialTransection'),
                ),  
                modules.ModelList(
                                  title='FUEL PELLET',
                                  column=1,
                                  models=('tragopan.models.FuelPellet','tragopan.models.FuelPelletType'),
                ), 
                modules.ModelList(
                                  title='FUEL ELEMENT',
                                  column=1,
                                  models=('tragopan.models.FuelElement','tragopan.models.FuelElementType'),
                ),
                modules.ModelList(
                                  title='FUEL ASSEMBLY',
                                  column=1,
                                  models=('tragopan.models.FuelAssemblyModel','tragopan.models.FuelAssemblyType','tragopan.models.FuelAssemblyRepository',),
                ),    
                              
            ],
        ))
        
        self.children.append(modules.Group(
            _('COMPONENT ASSEMBLY MODELING'),
            column=1,
            collapsible=True,
            css_classes=('grp-collapse grp-closed',),
            children = [
                modules.ModelList(
                                  title='BURNABLE POISON ASSEMBLY',
                                  column=1,
                                  models=('tragopan.models.BurnablePoisonRod','tragopan.models.BurnablePoisonAssembly'),
                   
                ),
                modules.ModelList(
                                  title='CONTROL ROD ASSEMBLY',
                                  column=1,
                                  models=('tragopan.models.ControlRodType','tragopan.models.ControlRodAssemblyType','tragopan.models.ControlRodCluster'),
                   
                )      
            ],
        ))
        
        self.children.append(modules.Group(
            _('PLANT INFO'),
            column=1,
            collapsible=True,
            css_classes=('grp-collapse grp-closed',),
            children = [
                modules.ModelList(
                                  title='BASIC INFO',
                                  column=1,
                                  models=('tragopan.models.ReactorModel','tragopan.models.Plant','tragopan.models.UnitParameter',),
                   
                ),
                modules.ModelList(
                                  title='OPERATION INFO',
                                  column=1,
                                  models=('tragopan.models.Cycle','tragopan.models.FuelAssemblyLoadingPattern',),
                   
                ),       
            ],
        ))
        
        self.children.append(modules.ModelList(
            css_classes=('grp-collapse grp-closed',),
            title='User Administration',
            column=2,
            models=('django.contrib.*',)
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=True,
            column=2,
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=3,
            children=[
                {
                    'title': _('FileBrowser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            column=3,
            children=[
                {
                    'title': _('OASIS Management'),
                    'url': '/admin/tragopan/',
                    'external': False,
                },
                {
                    'title': _('ADMIN log'),
                    'url': '/admin_log/',
                    'external': False,
                },

            ]
        ))
        


