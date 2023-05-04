from django.conf import settings
from django.contrib.gis.db import models
from django.urls import reverse
from django.utils import timezone
from users.models import User


SIDE_CHOICES = (
    ('L', 'Left'),
    ('R', 'Right'),
)


class TurtleSpecies(models.Model):
    scientific_name = models.CharField(max_length=128, unique=True)
    common_name = models.CharField(max_length=128, blank=True, null=True)
    old_species_code = models.CharField(max_length=2, blank=True, null=True)
    hide_dataentry = models.BooleanField(null=True)

    class Meta:
        verbose_name_plural = 'turtle species'
        ordering = ('common_name',)

    def __str__(self):
        if self.common_name:
            return f"{self.common_name} ({self.scientific_name})"
        else:
            return f"{self.scientific_name}"


class Location(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'turtle species'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Place(models.Model):
    location = models.ForeignKey(Location, models.PROTECT, related_name='places')
    name = models.CharField(max_length=128)
    rookery = models.BooleanField(null=True)
    beach_approach = models.CharField(max_length=64, blank=True, null=True)
    aspect = models.CharField(max_length=3, blank=True, null=True)
    point = models.PointField(srid=4326, blank=True, null=True)  # WGS 84
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('location__name', 'name')

    def __str__(self):
        if self.rookery:
            return f"{self.location.name} - {self.name} (rookery)"
        else:
            return f"{self.location.name} - {self.name}"


class EntryBatch(models.Model):
    entry_date = models.DateField(blank=True, null=True)
    entered_by = models.ForeignKey(User, models.PROTECT, blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    pr_date_convention = models.BooleanField(null=True)

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
        ('I', 'Indeterminate'),
    )
    STATUS_CHOICES = (
        ('A', 'Tag Turtles'),
        ('C', 'Captive'),
        ('E', 'Error (data not to be used)'),
        ('N', 'Non-tagged turtle'),
        ('P', 'Query new tagged'),
        ('Q', 'Query identity'),
        ('R', 'Re-entered population - Original Tag identity now unknown'),
        ('S', 'Salvage'),
        ('T', 'Tagged turtle - with full Tag history: first tag to last known'),
    )

    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    entered_by = models.ForeignKey(User, models.PROTECT, related_name='turtles_entered', blank=True, null=True)
    species = models.ForeignKey(TurtleSpecies, models.PROTECT, blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    # Query: is location a valid field for things that migrate and move around?
    location = models.ForeignKey(Location, models.PROTECT, related_name='turtles', blank=True, null=True)
    cause_of_death = models.CharField(max_length=2, choices=CAUSE_OF_DEATH_CHOICES, blank=True, null=True)
    re_entered_population = models.CharField(max_length=1, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    original_turtle_id = models.IntegerField(blank=True, null=True)
    entry_batch = models.ForeignKey(EntryBatch, models.PROTECT, blank=True, null=True)
    mund_id = models.CharField(max_length=255, blank=True, null=True)
    identification_confidence = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        if self.name and self.species:
            return f'{self.pk} {self.species.common_name} ({self.sex}) - {self.name}'
        elif self.species:
            return f'{self.pk} {self.species.common_name} ({self.sex})'
        else:
            return f'{self.pk} ({self.sex})'

    def get_absolute_url(self):
        return reverse('tagging:turtle_detail', kwargs={'pk': self.pk})

    def get_tags_description(self):
        tags = []
        for tag in self.tags.all():
            tags.append(str(tag))
        for tag in self.pit_tags.all():
            tags.append(f"{str(tag)} (pit tag)")
        return ", ".join(tags)


class TurtleObservation(models.Model):
    CONDITION_CHOICES = (
        ('D', 'Carcass - decomposed'),
        ('F', 'Carcass - fresh'),
        ('G', 'Good - fat'),
        ('H', 'Live & fit'),
        ('I', 'Injured but OK'),
        ('M', 'Moribund'),
        ('P', 'Poor - thin'),
        ('U', 'Floater - unable to dive'),
    )
    CLUTCH_COMPLETED_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('P', 'Possible'),
        ('U', 'Uncertain'),
        ('D', "Didn't check"),
    )
    EGG_COUNT_METHOD_CHOICES = (
        ('1Dr', 'Obs drop on laying'),
        ('2Ex', 'Exc & count post-lay'),
        ('3PH', 'Post-hatch nest exhumation'),
    )
    STATUS_CHOICES = (
        ('Initial Nesting', 'Initial Nesting'),
        ('Initial Sighting', 'Initial Sighting'),
        ('Remigrant', 'Remigrant'),
        ('Resighting', 'Resighting'),
    )
    DATE_CONVENTION_CHOICES = (
        ('C', 'Calendar'),
        ('E', 'Evening'),
        ('U', 'Unknown'),
    )
    BEACH_POSITION_CHOICES = (
        ('?', 'Not listed - Nesting event'),
        ('A', 'Above high water - Nesting event'),
        ('B', 'At high water - Nesting event'),
        ('C', 'Below high water - Nesting event'),
        ('D', 'Edge of spinifex (beach veg line) - Nesting event'),
        ('E', 'In spinifex (among beach veg) - Nesting event'),
    )
    ACTIVITY_CHOICES = (
        ('L', 'Arriving - Nesting'),
        ('K', 'Basking - on beach above waterline'),
        ('&', 'Captive animal'),
        ('W', 'Captured in water (reef or sea)'),
        ('V', 'Caught in fishing gear - Deceased'),
        ('Y', 'Caught in fishing gear - Released'),
        ('J', 'Check/edit these: only on VA records'),
        ('C', 'Climbing beach slope - Nesting'),
        ('H', 'Covering nest (filling in) - Nesting'),
        ('N', 'Courting'),
        ('E', 'Digging body hole - Nesting'),
        ('F', 'Excavating egg chamber - Nesting'),
        ('O', 'Free at sea'),
        ('Z', 'Hunted for food by Ab & others'),
        ('G', 'Laying eggs - confirmed observation - Nesting'),
        ('B', 'Leaving water - Nesting'),
        ('M', 'Mating'),
        ('D', 'Moving over bare sand (=beach) - Nesting'),
        ('P', 'Not listed - Nesting event'),
        ('Q', 'Not recorded in field'),
        ('R', 'Released to wild'),
        ('S', 'Rescued from stranding'),
        ('A', 'Resting at waters edge - Nesting'),
        ('I', 'Returning to water - Nesting'),
        ('X', 'Turtle dead'),
    )

    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    entered_by = models.ForeignKey(User, models.PROTECT, related_name='turtleobservations_entered', blank=True, null=True)
    turtle = models.ForeignKey(Turtle, models.PROTECT)
    observed = models.DateTimeField()
    observation_date_old = models.DateField(blank=True, null=True)
    date_convention = models.CharField(max_length=1, choices=DATE_CONVENTION_CHOICES)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, blank=True, null=True)
    alive = models.BooleanField(null=True)
    measurer = models.ForeignKey(User, models.PROTECT, related_name='measurer', blank=True, null=True)
    measurer_reporter = models.ForeignKey(User, models.PROTECT, related_name='measurer_reporter', blank=True, null=True)
    tagger = models.ForeignKey(User, models.PROTECT, related_name='tagger', blank=True, null=True)
    reporter = models.ForeignKey(User, models.PROTECT, related_name='reporter', blank=True, null=True)
    place = models.ForeignKey(Place, models.PROTECT, blank=True, null=True)
    place_description = models.TextField(blank=True, null=True)
    point = models.PointField(srid=4326, blank=True, null=True)  # WGS 84
    activity = models.CharField(max_length=1, choices=ACTIVITY_CHOICES, blank=True, null=True)
    beach_position = models.CharField(max_length=1, choices=BEACH_POSITION_CHOICES, blank=True, null=True)
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, blank=True, null=True)
    nesting = models.BooleanField(null=True)
    clutch_completed = models.CharField(max_length=1, choices=CLUTCH_COMPLETED_CHOICES, blank=True, null=True)
    number_of_eggs = models.IntegerField(blank=True, null=True)
    egg_count_method = models.CharField(max_length=3, choices=EGG_COUNT_METHOD_CHOICES, blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    original_observation_id = models.IntegerField(blank=True, null=True)
    entry_batch = models.ForeignKey(EntryBatch, models.PROTECT, blank=True, null=True)
    comment_fromrecordedtagstable = models.TextField(blank=True, null=True)
    scars_left = models.BooleanField(null=True)
    scars_right = models.BooleanField(null=True)
    transferid = models.IntegerField(blank=True, null=True)
    mund = models.BooleanField(null=True)
    scars_left_scale_1 = models.BooleanField(null=True, help_text='Left flipper scale closest to body')
    scars_left_scale_2 = models.BooleanField(null=True, help_text='Left flipper scale 2nd from body')
    scars_left_scale_3 = models.BooleanField(null=True, help_text='Left flipper scale 3rd from body')
    scars_right_scale_1 = models.BooleanField(null=True, help_text='Right flipper scale closest to body')
    scars_right_scale_2 = models.BooleanField(null=True, help_text='Right flipper scale 2nd from body')
    scars_right_scale_3 = models.BooleanField(null=True, help_text='Right flipper scale 3rd from body')
    cc_length_not_measured = models.BooleanField(null=True)
    cc_notch_length_not_measured = models.BooleanField(null=True)
    cc_width_not_measured = models.BooleanField(null=True)
    tagscarnotchecked = models.BooleanField(null=True)
    didnotcheckforinjury = models.BooleanField(null=True)
    corrected_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.status:
            return f'{self.pk} ({self.get_observed_awst().isoformat()}, {self.status})'
        else:
            return f'{self.pk} ({self.get_observed_awst().isoformat()})'

    def get_observed_awst(self):
        """Returns observation datetime in AWST.
        """
        if self.observed:
            return self.observed.astimezone(settings.AWST)
        else:
            return None

    def get_observed_utc(self):
        """Returns observation datetime in UTC.
        """
        if self.observed:
            return self.observed.astimezone(settings.UTC)
        else:
            return None

    def get_absolute_url(self):
        return reverse('tagging:turtleobservation_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('observed',)


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
        ('LOST', 'Tag lost off turtle'),
        ('Nil', 'No tag applied'),
        ('POOR', 'Poor fix on turtle'),
        ('QRY', 'Unknown if tag present'),
        ('RCL', 'Tag reclinched at obs'),
        ('RFX', 'Tag refixed at obs'),
        ('RMVD', 'Tag removed ex live turtle'),
        ('SAL', 'Salvage for reuse'),
        ('U', 'Unused tag'),
    )

    serial = models.CharField(max_length=64, unique=True)
    turtle = models.ForeignKey(Turtle, models.PROTECT, related_name='tags', blank=True, null=True)
    issue_location = models.CharField(max_length=128, blank=True, null=True)
    custodian = models.ForeignKey(User, models.PROTECT, related_name='tag_custodian', blank=True, null=True)
    field_person = models.ForeignKey(User, models.PROTECT, related_name='tag_field_person', blank=True, null=True)
    status = models.CharField(max_length=16, choices=TAG_STATUS_CHOICES, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    tag_order = models.ForeignKey(TagOrder, on_delete=models.PROTECT, blank=True, null=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.serial

    def delete(self, permanent=False, *args, **kwargs):
        '''Overide the delete method; in the absense of `permanent=True` being passed in, instead
        set the the turtle, status and side fields to None.
        '''
        if not permanent:
            self.turtle = None
            self.status = None
            self.side = None
            super(TurtleTag, self).save(*args, **kwargs)
        else:
            super(TurtleTag, self).delete(*args, **kwargs)

    def is_attached(self):
        '''Returns True if the tag is attached to a turtle, based on the status value.
        '''
        if self.status in ['ATT', 'RCL', 'RFX']:
            return True
        else:
            return False


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
    custodian = models.ForeignKey(User, models.PROTECT, related_name='pit_tag_custodian', blank=True, null=True)
    field_person = models.ForeignKey(User, models.PROTECT, related_name='pit_tag_field_person', blank=True, null=True)
    status = models.CharField(max_length=16, choices=PIT_TAG_STATUS_CHOICES, blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    tag_order = models.ForeignKey(TagOrder, on_delete=models.PROTECT, blank=True, null=True)
    batch_number = models.CharField(max_length=128, blank=True, null=True)
    box_number = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.serial

    def delete(self, permanent=False, *args, **kwargs):
        '''Overide the delete method; in the absense of `permanent=True` being passed in, instead
        set the the turtle and status fields to None.
        '''
        if not permanent:
            self.turtle = None
            self.status = None
            super(TurtlePitTag, self).save(*args, **kwargs)
        else:
            super(TurtlePitTag, self).delete(*args, **kwargs)

    def is_attached(self):
        '''Returns True if the tag is attached to a turtle, based on the status value.
        '''
        if self.status in ['ATT', 'POOR']:
            return True
        else:
            return False


class MeasurementType(models.Model):
    short_desc = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=128)
    unit = models.CharField(max_length=16, blank=True, null=True)
    minimum_value = models.FloatField(blank=True, null=True)
    maximum_value = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.unit:
            return f"{self.description} ({self.unit})"
        else:
            return self.description


class TurtleMeasurement(models.Model):
    observation = models.ForeignKey(TurtleObservation, models.PROTECT)
    measurement_type = models.ForeignKey(MeasurementType, models.PROTECT)
    value = models.FloatField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('observation', 'measurement_type')

    def __str__(self):
        if self.measurement_type.unit:
            return f"{self.value} {self.measurement_type.unit}"
        else:
            return f"{self.value}"


class TurtleDamage(models.Model):
    BODY_PART_CHOICES = (
        ('A', 'Carapace - entire'),
        ('B', 'Left front flipper'),
        ('C', 'Right front flipper'),
        ('D', 'Left rear flipper'),
        ('E', 'Right rear flipper'),
        ('H', 'Head'),
        ('I', 'Center mid-carapace'),
        ('J', 'Right front carapace'),
        ('K', 'Left front carapace'),
        ('L', 'Left rear carapace'),
        ('M', 'Right rear carapace'),
        ('N', 'Front mid-carapace'),
        ('O', 'Rear mid-carapace'),
        ('P', 'Plastron - entire'),
        ('T', 'Tail'),
        ('W', 'Whole animal'),
    )
    DAMAGE_CHOICES = (
        ('0', 'None significant'),
        ('1', 'Tip off - Flipper'),
        ('2', 'Lost from Nail - Flipper'),
        ('3', 'Lost half - Flipper'),
        ('4', 'Lost whole - Flipper'),
        ('5', 'Minor Wounds or cuts'),
        ('6', 'Major Wounds or cuts'),
        ('7', 'Deformity'),
    )
    CAUSE_CHOICES = (
        ('AG', 'Thick algae'),
        ('BB', 'Barnacles'),
        ('BP', 'Bite from predator'),
        ('BT', 'Bite from turtle'),
        ('MM', 'Thick mud'),
        ('OI', 'Other Impact'),
        ('PS', 'Parasites (other than barnacles)'),
        ('SD', 'Strike damage'),
    )
    observation = models.ForeignKey(TurtleObservation, models.PROTECT, related_name='damage')
    body_part = models.CharField(max_length=4, choices=BODY_PART_CHOICES)
    damage = models.CharField(max_length=4, choices=DAMAGE_CHOICES)
    cause = models.CharField(max_length=4, choices=CAUSE_CHOICES, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'turtle damage'

    def __str__(self):
        return f"{self.get_body_part_display()} ({self.get_damage_display()})"


class TurtleTagObservation(models.Model):
    STATUS_CHOICES = (
        ('#', 'Query number - Tag on'),
        ('0L', 'False Id as Lost'),
        ('A1', 'Applied new - OK fix'),
        ('A2', 'No tag applied'),
        ('AE', 'Applied new - end clinch noted'),
        ('M', 'Missing - obs record'),
        ('M1', 'Missing  - NOT obs'),
        ('N', 'Not Recorded'),
        ('OO', 'Open at Obs - Tag came off & not refixed'),
        ('OX', 'Open at Obs - Tag refixed'),
        ('P', 'Present Obs - & Read only'),
        ('P_ED', 'Present Obs - nr F edge & Read'),
        ('P_OK', 'Present Obs - OK fix & Read'),
        ('PX', 'Present Obs - Tag#s not read'),
        ('Q', 'Query present'),
        ('R', 'Removed by Obs'),
        ('RC', 'Insecure at Obs - reclinched in situ'),
        ('RQ', 'Insecure at Obs - Action ??'),
    )
    tag = models.ForeignKey(TurtleTag, on_delete=models.CASCADE, related_name="observations")
    observation = models.ForeignKey(TurtleObservation, on_delete=models.PROTECT, related_name="tag_observations")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True, null=True)
    position = models.SmallIntegerField(blank=True, null=True)  # Scale no. (1, 2, 3)
    barnacles = models.BooleanField(null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        d = self.observation.observed.strftime("%c")
        if self.status:
            return f"{self.tag.serial} ({d}) - {self.get_status_display()}"
        else:
            return f"{self.tag.serial} ({d})"


class TurtlePitTagObservation(models.Model):
    STATUS_CHOICES = (
        ('A1', 'Applied new - Read OK'),
        ('AE', 'Applied new - Did not read'),
        ('N', 'Not Recorded'),
        ('P', 'Present Obs - & Read OK'),
        ('P_OK', 'Present Obs - OK fix & Read'),
        ('PX', 'Present Obs - Tag#s not read'),
        ('RQ', 'Insecure at Obs - Action ??'),
    )
    POSITION_CHOICES = (
        ('LF', 'Left front'),
        ('RF', 'Right front'),
        ('LR', 'Left rear'),
        ('RR', 'Right rear'),
        ('Other', 'Other'),
    )
    tag = models.ForeignKey(TurtlePitTag, on_delete=models.CASCADE, related_name="observations")
    observation = models.ForeignKey(TurtleObservation, on_delete=models.PROTECT, related_name="pit_tag_observations")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, blank=True, null=True)
    position = models.CharField(max_length=8, choices=POSITION_CHOICES, blank=True, null=True)
    checked = models.BooleanField(null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        d = self.observation.observed.strftime("%c")
        if self.status:
            return f"{self.tag.serial} ({d}) - {self.get_status_display()}"
        else:
            return f"{self.tag.serial} ({d})"


class TurtleSample(models.Model):
    TISSUE_TYPE_CHOICES = (
        ('D', 'A-Tract contents'),
        ('9', 'Biopsy - gen'),
        ('1', 'Blood'),
        ('B', 'Brain'),
        ('E', 'Epibiota'),
        ('EGGs', 'Eggs'),
        ('8', 'Fat - depot storage'),
        ('D2', 'Faecal matter'),
        ('7', 'Gonad'),
        ('5', 'Heart'),
        ('K', 'Keratin - Fnail'),
        ('6', 'Kidney'),
        ('4', 'Liver'),
        ('3', 'Muscle - Pectoral'),
        ('S', 'Skeletal'),
        ('2', 'Skin'),
        ('W', 'Whole animal'),
    )
    observation = models.ForeignKey(TurtleObservation, on_delete=models.PROTECT, related_name="samples")
    tissue_type = models.CharField(max_length=8, choices=TISSUE_TYPE_CHOICES)
    label = models.CharField(max_length=64, blank=True, null=True)
    sample_date = models.DateField(blank=True, null=True)
    arsenic = models.FloatField(blank=True, null=True)
    selenium = models.FloatField(blank=True, null=True)
    zinc = models.FloatField(blank=True, null=True)
    cadmium = models.FloatField(blank=True, null=True)
    copper = models.FloatField(blank=True, null=True)
    lead = models.FloatField(blank=True, null=True)
    mercury = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        d = self.observation.observed.strftime("%c")
        if self.label:
            return f"{self.get_tissue_type_display()} ({d}) - {self.label}"
        else:
            return f"{self.get_tissue_type_display()} ({d})"


class TurtleIdentification(models.Model):
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
        ('WAMusR', 'WA Museum R#'),('A', 'Qld - monel A series tag'),
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

    turtle = models.ForeignKey(Turtle, models.PROTECT)
    identification_type = models.CharField(max_length=32, choices=IDENTIFICATION_TYPE_CHOICES)
    identifier = models.CharField(max_length=64)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.identifier} ({self.get_identification_type_display()})"
