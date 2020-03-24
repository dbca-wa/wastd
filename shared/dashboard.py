"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'wastd.dashboard.AdminDashboard'
"""

from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class AdminDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """
    class Media:
        css = {
            'all': (
                'css/grappelli_dashboard.css',
            ),
        }

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Col1: TSC
        self.children.append(modules.Group(
            _('Threatened Species and Communities'),
            column=1,
            collapsible=True,
            children=[
                modules.AppList(
                    _('Taxonomy'),
                    column=1,
                    collapsible=True,
                    models=('taxonomy.models.Taxon',
                            'taxonomy.models.HbvSupra',
                            'taxonomy.models.Community',),
                ),
                modules.AppList(
                    _('Conservation Listings'),
                    column=1,
                    css_classes=('collapse',),
                    models=(
                        'conservation.models.ConservationList',
                        'conservation.models.ConservationCategory',
                        'conservation.models.ConservationCriterion',
                        'conservation.models.CommunityConservationListing',
                        'conservation.models.TaxonConservationListing',
                    ),
                ),

                modules.AppList(
                    _('Conservation Threats and Actions'),
                    column=1,
                    css_classes=('collapse',),
                    models=(
                        'conservation.models.ConservationThreatCategory',
                        'conservation.models.ConservationActionCategory',
                        'conservation.models.ConservationThreat',
                        'conservation.models.ConservationAction',
                        'conservation.models.ConservationActivity',
                    ),
                ),
                modules.AppList(
                    _('Conservation Plans and Documents'),
                    column=1,
                    css_classes=('collapse',),
                    models=(
                        'conservation.models.Document',
                    ),
                ),

                modules.AppList(
                    _('Occurrences'),
                    column=1,
                    css_classes=('collapse',),
                    models=(
                        'occurrence.models.TaxonAreaEncounter',
                        'occurrence.models.CommunityAreaEncounter',
                    ),
                ),
                modules.AppList(
                    _('Occurrence Lookups'),
                    column=1,
                    css_classes=('collapse grp-closed',),
                    models=('occurrence.models.*',),
                    exclude=(
                        'occurrence.models.TaxonAreaEncounter',
                        'occurrence.models.CommunityAreaEncounter',
                    ),
                )

            ]
        ))

        # Col2: WAStD
        self.children.append(modules.Group(
            _('WA Sea Turtle Database'),
            column=2,
            collapsible=True,
            children=[
                modules.AppList(
                    _('Places and Surveys'),
                    column=2,
                    collapsible=True,
                    models=(
                        'wastd.observations.models.Area',
                        'wastd.observations.models.Survey', ),
                ),
                modules.AppList(
                    _('Encounters'),
                    column=2,
                    collapsible=True,
                    models=(
                        'wastd.observations.models.Encounter',
                        'wastd.observations.models.AnimalEncounter',
                        'wastd.observations.models.TurtleNestEncounter',
                        'wastd.observations.models.LineTransectEncounter',
                        'wastd.observations.models.LoggerEncounter',
                    ),
                ),
                modules.AppList(
                    _('Encounter Observations'),
                    column=2,
                    collapsible=True,
                    models=(
                        # Adult animals:
                        'wastd.observations.models.TagObservation',
                        # TurtleMorphometricObservation
                        # TurtleDamageObservation
                        #
                        # Turtle Nests:
                        'wastd.observations.models.TurtleNestObservation',
                        'wastd.observations.models.TurtleNestDisturbanceObservation',
                        'wastd.observations.models.NestTagObservation',
                        # TurtleHatchlingEmergenceObservation
                        # TurtleHatchlingEmergenceOutlierObservation
                        # LightSourceObservation
                        # HatchlingMorphometricObservation
                        # DugongMorphometricObservation

                        # LineTransects:
                        # TrackTallyObservation
                        # TurtleNestDisturbanceTallyObservation

                        # Loggers
                        'wastd.observations.models.LoggerEncounter',
                        # TemperatureLoggerSettings
                        # DispatchRecord
                        # TemperatureLoggerDeployment

                    ),
                ),

            ]
        ))

        # Col3: Admin
        self.children.append(modules.Group(
            _('Administration'),
            column=3,
            collapsible=True,
            children=[
                modules.AppList(
                    _('User access management'),
                    column=2,
                    css_classes=('collapse grp-closed',),
                    collapsible=True,
                    models=('wastd.users.*', 'django.contrib.*', ),
                ),
                modules.AppList(
                    _('WACensus Staging Area'),
                    column=1,
                    css_classes=('collapse grp-closed',),
                    collapsible=True,
                    models=('taxonomy.models.Hbv*',),
                ),
            ]
        ))

        # # append an app list module for "Administration"
        # self.children.append(modules.ModelList(
        #     _('ModelList: Administration'),
        #     column=1,
        #     collapsible=False,
        #     models=('django.contrib.*',),
        # ))

        # # append another link list module for "support".
        # self.children.append(modules.LinkList(
        #     _('Media Management'),
        #     column=2,
        #     children=[
        #         {
        #             'title': _('FileBrowser'),
        #             'url': '/admin/filebrowser/browse/',
        #             'external': False,
        #         },
        #     ]
        # ))

        # # append another link list module for "support".
        # self.children.append(modules.LinkList(
        #     _('Support'),
        #     column=2,
        #     children=[
        #         {
        #             'title': _('Django Documentation'),
        #             'url': 'http://docs.djangoproject.com/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Grappelli Documentation'),
        #             'url': 'http://packages.python.org/django-grappelli/',
        #             'external': True,
        #         },
        #         {
        #             'title': _('Grappelli Google-Code'),
        #             'url': 'http://code.google.com/p/django-grappelli/',
        #             'external': True,
        #         },
        #     ]
        # ))

        # # append a feed module
        # self.children.append(modules.Feed(
        #     _('Latest Django News'),
        #     column=2,
        #     feed_url='http://www.djangoproject.com/rss/weblog/',
        #     limit=5
        # ))

        # # append a recent actions module
        # self.children.append(modules.RecentActions(
        #     _('Recent Actions'),
        #     limit=5,
        #     collapsible=False,
        #     column=3,
        # ))
