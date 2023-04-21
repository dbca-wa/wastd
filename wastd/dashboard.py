from grappelli.dashboard import modules, Dashboard


class AdminDashboard(Dashboard):

    def init_with_context(self, context):
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
                "Animal Tagging",
                column=3,
                children=[
                    modules.AppList(
                        "Turtle tagging records",
                        models=(
                            "tagging.models.Turtle",
                            "tagging.models.TurtleObservation",
                            "tagging.models.TurtleTag",
                            "tagging.models.TurtlePitTag",
                            "tagging.models.TagOrder",
                            "tagging.models.TurtleSample",
                        )
                    )
                ],
            )
        )
