# Generated by Django 4.2.11 on 2024-04-19 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("observations", "0013_alter_encounter_polymorphic_ctype_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="observation",
            options={"ordering": ("-pk",)},
        ),
        migrations.AlterField(
            model_name="animalencounter",
            name="cause_of_death_confidence",
            field=models.CharField(
                choices=[
                    ("na", "Not applicable"),
                    ("guess", "Guess based on insufficient evidence"),
                    ("certain", "Certainty based on local evidence"),
                    ("expert-opinion", "Expert opinion based on available evidence"),
                    ("validated", "Validated by authoritative source"),
                ],
                default="na",
                help_text="What is the cause of death, if known, based on?",
                max_length=300,
            ),
        ),
        migrations.AlterField(
            model_name="turtlenestdisturbanceobservation",
            name="disturbance_cause_confidence",
            field=models.CharField(
                choices=[
                    ("na", "Not applicable"),
                    ("guess", "Guess based on insufficient evidence"),
                    ("certain", "Certainty based on local evidence"),
                    ("expert-opinion", "Expert opinion based on available evidence"),
                    ("validated", "Validated by authoritative source"),
                ],
                default="na",
                help_text="What is the choice of disturbance cause based on?",
                max_length=300,
                verbose_name="Disturbance cause choice confidence",
            ),
        ),
        migrations.AlterField(
            model_name="turtlenestdisturbanceobservation",
            name="disturbance_severity",
            field=models.CharField(
                choices=[
                    ("negligible", "Negligible disturbance"),
                    ("partly", "Nest partly destroyed"),
                    ("completely", "Nest completely destroyed"),
                    ("na", "Nest in indeterminate condition"),
                ],
                default="na",
                help_text="The impact of the disturbance on nest viability.",
                max_length=300,
            ),
        ),
    ]