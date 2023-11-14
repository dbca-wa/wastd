from grappelli.dashboard import modules, Dashboard


class AdminDashboard(Dashboard):

    def init_with_context(self, context):
        self.children.append(
            modules.Group(
                "WA Sea Turtle Database",
                column=1,
                children=[
                    modules.AppList(
                        "Places, campaigns, surveys",
                        models=(
                            "observations.models.Area",
                            "observations.models.Campaign",
                            "observations.models.Survey",
                        ),
                    ),
                    modules.AppList(
                        "Encounters and observations",
                        models=(
                            "observations.models.AnimalEncounter",
                            "observations.models.TurtleNestEncounter",
                        ),
                    ),
                ],
            )
        )

        self.children.append(
            modules.Group(
                "Turtle tagging",
                column=2,
                children=[
                    modules.AppList(
                        "Tag management",
                        models=(
                            "turtle_tags.models.Turtle",
                            "turtle_tags.models.TurtleTag",
                            "turtle_tags.models.TagPurchaseOrder",
                        ),
                    ),
                ],
            )
        )

        self.children.append(
            modules.Group(
                "Marine mammal incidents",
                column=2,
                children=[
                    modules.AppList(
                        "Incidents management",
                        models=(
                            "marine_mammal_incidents.models.Incident",
                            "marine_mammal_incidents.models.Species",
                            "marine_mammal_incidents.models.Uploaded_file"
                        ),
                    ),
                ],
            )
        )

        self.children.append(
            modules.Group(
                "User administration",
                column=3,
                children=[
                    modules.AppList(
                        "User access management",
                        models=(
                            "users.models.User",
                            "users.models.Organisation",
                        ),
                    ),
                ],
            )
        )
