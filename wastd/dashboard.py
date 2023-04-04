from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class AdminDashboard(Dashboard):

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # Col: WAStD
        self.children.append(
            modules.Group(
                "WA Sea Turtle Database",
                column=1,
                #collapsible=True,
                children=[
                    modules.AppList(
                        "Places, Campaigns, Surveys",
                        #column=2,
                        #collapsible=True,
                        models=(
                            "observations.models.Area",
                            "observations.models.Campaign",
                            "observations.models.Survey",
                        ),
                    ),
                    modules.AppList(
                        "Encounters",
                        #column=2,
                        #collapsible=True,
                        models=(
                            "observations.models.Encounter",
                            "observations.models.AnimalEncounter",
                            "observations.models.TurtleNestEncounter",
                            #"observations.models.LineTransectEncounter",
                        ),
                    ),
                ],
            )
        )

        # Col: User Admin
        self.children.append(
            modules.Group(
                "User Administration",
                column=2,
                #collapsible=True,
                children=[
                    modules.AppList(
                        "User access management",
                        #column=2,
                        #css_classes=("collapse grp-closed",),
                        #collapsible=True,
                        models=(
                            "users.*",
                            "django.contrib.*",
                        ),
                    ),
                ],
            )
        )

        self.children.append(
            modules.Group(
                "Turtle Tagging Database",
                column=3,
                children=[
                    modules.AppList(
                        "Turtle tagging records",
                        models=(
                            "turtle_tag.models.Turtle",
                            "turtle_tag.models.TurtleObservation",
                            "turtle_tag.models.TurtleTag",
                            "turtle_tag.models.TurtlePitTag",
                        )
                    )
                ],
            )
        )
