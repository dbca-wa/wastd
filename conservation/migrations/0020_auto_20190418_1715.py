# Generated by Django 2.1.7 on 2019-04-18 09:15

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('conservation', '0019_auto_20190410_1329'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TaxonGazettal',
            new_name='TaxonConservationListing',
        ),
        migrations.RenameModel(
            old_name='CommunityGazettal',
            new_name='CommunityConservationListing',
        ),
    ]
