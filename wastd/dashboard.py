from django.utils.translation import gettext_lazy as _
from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class AdminDashboard(Dashboard):

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Col: WAStD
        self.children.append(
            modules.Group(
                _("WA Sea Turtle Database"),
                column=2,
                collapsible=True,
                children=[
                    modules.AppList(
                        _("Places, Campaigns, Surveys"),
                        column=2,
                        collapsible=True,
                        models=(
                            "observations.models.Area",
                            "observations.models.Campaign",
                            "observations.models.Survey",
                        ),
                    ),
                    modules.AppList(
                        _("Encounters"),
                        column=2,
                        collapsible=True,
                        models=(
                            "observations.models.Encounter",
                            "observations.models.AnimalEncounter",
                            "observations.models.TurtleNestEncounter",
                            "observations.models.LineTransectEncounter",
                        ),
                    ),
                    modules.AppList(
                        _("Encounter Observations"),
                        column=2,
                        collapsible=True,
                        models=(
                            "observations.models.MediaAttachment",
                            # Adult animals:
                            "observations.models.TagObservation",
                            "observations.models.TurtleMorphometricObservation",
                            "observations.models.TurtleDamageObservation",
                            "observations.models.DugongMorphometricObservation",
                            # Turtle Nests:
                            "observations.models.TurtleNestObservation",
                            "observations.models.TurtleNestDisturbanceObservation",
                            "observations.models.TurtleHatchlingEmergenceObservation",
                            "observations.models.TurtleHatchlingEmergenceOutlierObservation",
                            "observations.models.LightSourceObservation",
                            "observations.models.HatchlingMorphometricObservation",
                            "observations.models.NestTagObservation",
                            # LineTransects:
                            "observations.models.TrackTallyObservation",
                            "observations.models.TurtleNestDisturbanceTallyObservation",
                            # Loggers
                            "observations.models.LoggerObservation",
                            "observations.models.TemperatureLoggerSettings",
                            "observations.models.DispatchRecord",
                            "observations.models.TemperatureLoggerDeployment",
                        ),
                    ),
                ],
            )
        )

        # Col: Admin
        self.children.append(
            modules.Group(
                _("Administration"),
                column=3,
                collapsible=True,
                children=[
                    modules.AppList(
                        _("User access management"),
                        column=2,
                        css_classes=("collapse grp-closed",),
                        collapsible=True,
                        models=(
                            "users.*",
                            "django.contrib.*",
                        ),
                    ),
                ],
            )
        )
