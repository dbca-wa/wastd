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
                children=[
                    modules.AppList(
                        "Places, Campaigns, Surveys",
                        models=(
                            "observations.models.Area",
                            "observations.models.Campaign",
                            "observations.models.Survey",
                        ),
                    ),
                    modules.AppList(
                        "Encounters",
                        models=(
                            "observations.models.Encounter",
                            "observations.models.AnimalEncounter",
                            "observations.models.TurtleNestEncounter",
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
                children=[
                    modules.AppList(
                        "User access management",
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
                "Tagging",
                column=3,
                children=[
                    modules.AppList(
                        "Turtle tagging",
                        models=(
                            "tagging.models.Turtle",
                            "tagging.models.TurtleObservation",
                            "tagging.models.TurtleTag",
                            "tagging.models.TurtlePitTag",
                        )
                    )
                ],
            )
        )
