# Generated by Django 3.2.20 on 2023-07-18 02:51

from django.db import migrations, models
import observations.models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0005_auto_20230710_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignmediaattachment',
            name='campaign',
        ),
        migrations.DeleteModel(
            name='SiteVisitStartEnd',
        ),
        migrations.AlterField(
            model_name='survey',
            name='end_photo',
            field=models.FileField(blank=True, help_text='Site conditions at end of survey.', max_length=500, null=True, upload_to=observations.models.survey_media, verbose_name='Site photo end'),
        ),
        migrations.DeleteModel(
            name='CampaignMediaAttachment',
        ),
    ]
