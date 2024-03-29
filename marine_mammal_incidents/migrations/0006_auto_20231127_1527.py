# Generated by Django 3.2.21 on 2023-11-27 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marine_mammal_incidents', '0005_auto_20231127_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='length',
            field=models.DecimalField(decimal_places=2, help_text='in centimeters', max_digits=10),
        ),
        migrations.AlterField(
            model_name='incident',
            name='weight',
            field=models.DecimalField(decimal_places=2, help_text='in kilograms', max_digits=10),
        ),
    ]
