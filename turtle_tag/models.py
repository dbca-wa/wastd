from datetime import datetime
from django.conf import settings
from django.contrib.gis.db import models
from django.urls import reverse
from users.models import User


IDENTIFICATION_TYPE_CHOICES = (
    ('A', 'Qld - monel A series tag'),
    ('Acoustic', 'Acoustic'),
    ('ATLANTIS', 'Atlantis [now closed]'),
    ('CA', 'CofAust - titanium tag'),
    ('CT', 'Cayman - juvenile tag'),
    ('CTD', 'Conductivity - Temp - Depth SRDL'),
    ('ENT/REL', 'Untagged turtle - live release from entanglement'),
    ('ENT/SAL', 'Untagged turtle - salvage from entanglement'),
    ('FISH/DECD', 'Untagged turtle - Fishery capture victim'),
    ('FREE/OBS', 'Untagged turtle - live obs'),
    ('I', 'HIMB - Inconel tag'),
    ('K', 'Qld - titanium K series tag'),
    ('PTT', 'PT transmitter'),
    ('PZ ID', 'Perth Zoo Vets - case ID'),
    ('RREC', 'Naragebup rehab'),
    ('SFU/FIU', 'RotoTag'),
    ('SRDL', 'Satellite Relay Data Logger (SRDL)/?CATS-SATags'),
    ('STRAND/SAL', 'Untagged turtle - stranding victim'),
    ('T', 'Qld - titanium T series tag'),
    ('UWW', 'Underwater World [now AQWA]'),
    ('WAMusR', 'WA Museum R#'),
)


class TurtleSpecies(models.Model):
    scientific_name = models.CharField(max_length=128, unique=True)
    common_name = models.CharField(max_length=128, blank=True, null=True)
    old_species_code = models.CharField(max_length=2, blank=True, null=True)
    hide_dataentry = models.BooleanField()

    class Meta:
        verbose_name_plural = 'turtle species'

    def __str__(self):
        if self.common_name:
            return f"{self.scientific_name} ({self.common_name})"
        else:
            return f"{self.scientific_name}"


class TurtleStatus(models.Model):
    description = models.CharField(max_length=128)
    new_tag_list = models.BooleanField()

    class Meta:
        verbose_name_plural = 'turtle statuses'

    def __str__(self):
        return self.description


class Location(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Place(models.Model):
    location = models.ForeignKey(Location, models.PROTECT, related_name='places')
    name = models.CharField(max_length=128, blank=True, null=True)
    rookery = models.BooleanField(null=True)
    beach_approach = models.CharField(max_length=50, blank=True, null=True)
    aspect = models.CharField(max_length=3, blank=True, null=True)
    point = models.PointField(srid=4326, blank=True, null=True)  # WGS 84
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return f"{self.location.name} - {self.name}"
        else:
            return f"{self.location.name}"


class Activity(models.Model):
    description = models.CharField(max_length=128)
    nesting = models.CharField(max_length=128)
    new_code = models.CharField(max_length=255, blank=True, null=True)
    display_observation = models.BooleanField()

    class Meta:
        verbose_name_plural = 'activities'

    def __str__(self):
        return self.description


class BeachPosition(models.Model):
    description = models.CharField(max_length=128)
    new_code = models.CharField(max_length=128)

    def __str__(self):
        return self.description


class EntryBatch(models.Model):
    entry_date = models.DateField(blank=True, null=True)
    entered_person = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    pr_date_convention = models.BooleanField()

    class Meta:
        verbose_name_plural = 'entry batches'


class Turtle(models.Model):

    CAUSE_OF_DEATH_CHOICES = (
        ('BS', 'Boat strike'),
        ('DR', 'Drowning'),
        ('FI', 'Fishery'),
        ('HA', 'Handling accident'),
        ('IH', 'Indigenous hunt'),
        ('MO', 'Misorientation on beach'),
        ('NC', 'Natural causes'),
        ('SH', 'Shark predation'),
        ('UK', 'Unknown'),
    )
    SEX_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('U', 'Unknown'),
    )

    species = models.ForeignKey(TurtleSpecies, models.PROTECT, blank=True, null=True)
    identification_confidence = models.CharField(max_length=1, blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    status = models.ForeignKey(TurtleStatus, models.PROTECT, blank=True, null=True)
    location = models.ForeignKey(Location, models.PROTECT, related_name='turtles', blank=True, null=True)
    cause_of_death = models.CharField(max_length=2, choices=CAUSE_OF_DEATH_CHOICES, blank=True, null=True)
    re_entered_population = models.CharField(max_length=1, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    entered_by = models.CharField(max_length=50, blank=True, null=True)
    date_entered = models.DateField(blank=True, null=True)
    original_turtle_id = models.IntegerField(blank=True, null=True)
    entry_batch_id = models.IntegerField(blank=True, null=True)
    tag = models.CharField(max_length=255, blank=True, null=True)
    mund_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        if self.name:
            return f'{self.pk}: {self.species.common_name} ({self.sex}) - {self.name}'
        else:
            return f'{self.pk}: {self.species.common_name} ({self.sex})'

    def get_absolute_url(self):
        return reverse('turtle_tag:turtle_detail', kwargs={'pk': self.pk})


class TurtleObservation(models.Model):

    CONDITION_CHOICES = (
        ('D', 'Carcase - decomposed'),
        ('F', 'Carcase - fresh'),
        ('G', 'Good - fat'),
        ('H', 'Live & fit'),
        ('I', 'Injured but OK'),
        ('M', 'Moribund'),
        ('P', 'Poor - thin'),
        ('U', 'Floater - unable to dive'),
    )
    EGG_COUNT_METHOD_CHOICES = (
        ('1Dr', 'Obs drop on laying'),
        ('2Ex', 'Exc & count post-lay'),
        ('3PH', 'Post-hatch nest exhumation'),
    )

    turtle = models.ForeignKey(Turtle, models.PROTECT)
    observation_datetime = models.DateTimeField()
    observation_date_old = models.DateField(blank=True, null=True)
    alive = models.BooleanField(null=True)
    measurer_person = models.ForeignKey(User, models.SET_NULL, related_name='measurer', blank=True, null=True)
    measurer_reporter_person = models.ForeignKey(User, models.SET_NULL, related_name='measurer_reporter', blank=True, null=True)
    tagger_person = models.ForeignKey(User, models.SET_NULL, related_name='tagger', blank=True, null=True)
    reporter_person = models.ForeignKey(User, models.SET_NULL, related_name='reporter', blank=True, null=True)
    place = models.ForeignKey(Place, models.PROTECT, blank=True, null=True)
    place_description = models.TextField(blank=True, null=True)
    point = models.PointField(srid=4326, blank=True, null=True)  # WGS 84
    activity = models.ForeignKey(Activity, models.PROTECT, blank=True, null=True)
    beach_position = models.ForeignKey(BeachPosition, models.PROTECT, blank=True, null=True)
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, blank=True, null=True)
    nesting = models.BooleanField(null=True)
    clutch_completed = models.CharField(max_length=1, blank=True, null=True)
    number_of_eggs = models.IntegerField(blank=True, null=True)
    egg_count_method = models.CharField(max_length=3, choices=EGG_COUNT_METHOD_CHOICES, blank=True, null=True)
    measurements = models.CharField(max_length=1)
    action_taken = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    entered_by = models.CharField(max_length=50, blank=True, null=True)
    date_entered = models.DateField(blank=True, null=True)
    original_observation_id = models.IntegerField(blank=True, null=True)
    entry_batch = models.ForeignKey(EntryBatch, models.PROTECT, blank=True, null=True)
    comment_fromrecordedtagstable = models.TextField(blank=True, null=True)
    scars_left = models.BooleanField()
    scars_right = models.BooleanField()
    other_tags = models.TextField(blank=True, null=True)
    other_tags_identification_type = models.CharField(max_length=10, choices=IDENTIFICATION_TYPE_CHOICES, blank=True, null=True)
    transferid = models.IntegerField(blank=True, null=True)
    mund = models.BooleanField()
    entered_by_person = models.ForeignKey(User, models.SET_NULL, related_name='entered_by', blank=True, null=True)
    scars_left_scale_1 = models.BooleanField()
    scars_left_scale_2 = models.BooleanField()
    scars_left_scale_3 = models.BooleanField()
    scars_right_scale_1 = models.BooleanField()
    scars_right_scale_2 = models.BooleanField()
    scars_right_scale_3 = models.BooleanField()
    cc_length_not_measured = models.BooleanField()
    cc_notch_length_not_measured = models.BooleanField()
    cc_width_not_measured = models.BooleanField()
    tagscarnotchecked = models.BooleanField()
    didnotcheckforinjury = models.BooleanField()
    date_convention = models.CharField(max_length=1)
    observation_status = models.CharField(max_length=128, blank=True, null=True)
    corrected_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.observation_status:
            return f'{self.pk} ({self.get_observation_datetime_awst().isoformat()}) {(self.observation_status)}'
        else:
            return f'{self.pk} ({self.get_observation_datetime_awst().isoformat()})'

    def get_observation_datetime_awst(self):
        """Returns observation datetime in AWST.
        """
        if self.observation_datetime:
            return self.observation_datetime.astimezone(settings.AWST)
        else:
            return None

    def get_observation_datetime_utc(self):
        """Returns observation datetime in UTC.
        """
        if self.observation_datetime:
            return self.observation_datetime.astimezone(settings.UTC)
        else:
            return None


class TagOrder(models.Model):
    order_number = models.CharField(max_length=64)
    order_date = models.DateField(blank=True, null=True)
    tag_prefix = models.CharField(max_length=16, blank=True, null=True)
    start_tag_number = models.IntegerField(blank=True, null=True)
    end_tag_number = models.IntegerField(blank=True, null=True)
    total_tags = models.IntegerField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    paid_by = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.order_number


class TurtleTag(models.Model):

    TAG_STATUS_CHOICES = (
        ('0BRK', '0 BRK - Tag Broken'),
        ('1DD', '1 DUD - Tag U/s'),
        ('2DB', '2 DUDB - Tag U/s break'),
        ('3DC', '3 DUDC - Clinch NO turtle'),
        ('4DM', '4 DUDM - Mfr error'),
        ('5DROP', '5 DROP - Lost on beach'),
        ('6NAD', '6 NOAD - Mfr error'),
        ('7NSP', '7 NOSP - Supply error'),
        ('8YY', 'Tag unknown fate'),
        ('ATT', 'Tag attached to turtle'),
        ('DET', 'Tag taken from dead turtle'),
        ('LOST', 'Tag Lost off turtle'),
        ('Nil', 'No tag applied'),
        ('POOR', 'Poor fix on turtle'),
        ('QRY', 'Unknown if tag present'),
        ('RCL', 'Tag reclinched at Obs'),
        ('RFX', 'Tag refixed at Obs'),
        ('RMVD', 'Tag removed ex live turtle'),
        ('SAL', 'Salvage for reuse'),
        ('U', 'Unused Tag'),
    )

    serial = models.CharField(max_length=64, unique=True)
    turtle = models.ForeignKey(Turtle, models.PROTECT, related_name='tags', blank=True, null=True)
    issue_location = models.CharField(max_length=128, blank=True, null=True)
    custodian = models.ForeignKey(User, models.SET_NULL, related_name='tag_custodian', blank=True, null=True)
    status = models.CharField(max_length=16, choices=TAG_STATUS_CHOICES, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    field_person = models.ForeignKey(User, models.SET_NULL, related_name='tag_field_person', blank=True, null=True)
    tag_order = models.ForeignKey(TagOrder, on_delete=models.PROTECT, blank=True, null=True)
    side = models.CharField(max_length=1, blank=True, null=True)


class TurtlePitTag(models.Model):

    PIT_TAG_STATUS_CHOICES = (
        ('1DD', '1 DUD - Tag U/s'),
        ('2DB', '2 DUDB - Tag U/s break'),
        ('3DC', '3 DUDC - Clinch not on turtle'),
        ('4DM', '4 DUDM - Mfr error'),
        ('5DROP', '5 DROP - Lost on beach'),
        ('8YY', 'Tag unknown fate'),
        ('ATT', 'Tag attached to turtle - Read OK'),
        ('DET', 'Tag taken from dead turtle'),
        ('Nil', 'No tag applied'),
        ('POOR', 'Applied new - Did not read'),
        ('QRY', 'Unknown if PIT present'),
        ('RMVD', 'Tag removed ex live turtle'),
        ('SAL', 'Salvaged'),
        ('U', 'Unused PIT'),
    )

    serial = models.CharField(max_length=64, unique=True)
    turtle = models.ForeignKey(Turtle, models.PROTECT, related_name='pit_tags', blank=True, null=True)
    issue_location = models.CharField(max_length=128, blank=True, null=True)
    custodian = models.ForeignKey(User, models.SET_NULL, related_name='pit_tag_custodian', blank=True, null=True)
    status = models.CharField(max_length=16, choices=PIT_TAG_STATUS_CHOICES, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    field_person = models.ForeignKey(User, models.SET_NULL, related_name='pit_tag_field_person', blank=True, null=True)
    tag_order = models.ForeignKey(TagOrder, on_delete=models.PROTECT, blank=True, null=True)
    batch_number = models.CharField(max_length=128, blank=True, null=True)
    box_number = models.CharField(max_length=128, blank=True, null=True)
