from django.db import models
from django.urls import reverse
from django.utils import timezone

from observations.models import AnimalEncounter,TagObservation
from users.models import User

SOURCE_CHOICES = (
    ("direct", "Direct entry"),
    ("wamtram", "WAMTRAM database"),
)


class Turtle(models.Model):
    """Metadata record related to an individual tagged turtle.
    """

    TURTLE_SPECIES_DEFAULT = "cheloniidae-fam"
    TURTLE_SPECIES_CHOICES = (
        ("natator-depressus", "Natator depressus (Flatback turtle)"),
        ("chelonia-mydas", "Chelonia mydas (Green turtle)"),
        ("eretmochelys-imbricata", "Eretmochelys imbricata (Hawksbill turtle)"),
        ("caretta-caretta", "Caretta caretta (Loggerhead turtle)"),
        ("lepidochelys-olivacea", "Lepidochelys olivacea (Olive ridley turtle)"),
        ("dermochelys-coriacea", "Dermochelys coriacea (Leatherback turtle)"),
        ("chelonia-mydas-agassazzi", "Chelonia mydas agassazzi (Black turtle or East Pacific Green)"),
        (TURTLE_SPECIES_DEFAULT, "Cheloniidae (Unidentified turtle)"),
    )
    UNKNOWN_VALUE = "unknown"
    UNKNOWN_CHOICE = (UNKNOWN_VALUE, "Unknown")
    SEX_CHOICES = (
        UNKNOWN_CHOICE,
        ("male", "Male"),
        ("female", "Female"),
        ("intersex", "Hermaphrodite or intersex"),
    )

    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    entered_by = models.ForeignKey(User, models.PROTECT, blank=True, null=True)
    source = models.CharField(
        max_length=256,
        choices=SOURCE_CHOICES,
        default="direct",
        db_index=True,
    )
    source_id = models.CharField(
        max_length=256,
        db_index=True,
        default="na",
        help_text="The ID of this record in the original source (if applicable)",
    )
    species = models.CharField(
        max_length=256,
        choices=TURTLE_SPECIES_CHOICES,
        default=TURTLE_SPECIES_DEFAULT,
        db_index=True,
    )
    sex = models.CharField(
        max_length=256,
        choices=SEX_CHOICES,
        default=UNKNOWN_VALUE,
        db_index=True,
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.name and self.species:
            return f"{self.get_species_display()}, {self.get_sex_display()} - {self.name}"
        elif self.species:
            return f"{self.get_species_display()}, {self.get_sex_display()}"
        else:
            return f"{self.get_sex_display()}"

    def get_absolute_url(self):
        return reverse('turtle_tags:turtle_detail', kwargs={'pk': self.pk})

    def get_tags_description(self):
        tags = []
        for tag in self.turtletag_set.all():
            tags.append(str(tag))
        return ", ".join(tags)

    def get_tag_observations(self):
        """Return the queryset of TagObservation records for this turtle.
        """
        tag_observation_pks = []

        for tag in self.turtletag_set.all():
            tag_observation_pks = tag_observation_pks + list(TagObservation.objects.filter(tag_type=tag.tag_type, name=tag.serial).values_list('pk', flat=True))

        return TagObservation.objects.filter(pk__in=tag_observation_pks)

    def get_encounters(self):
        observations = self.get_tag_observations()
        return AnimalEncounter.objects.filter(pk__in=observations.values_list("encounter", flat=True))

    def get_newest_encounter(self):
        """Return the most-recent encounter with this turtle, based upon TagObservation records.
        """
        observations = self.get_tag_observations()
        if observations:
            return observations.order_by('-encounter__when').first().encounter
        else:
            return None


class TagPurchaseOrder(models.Model):
    """Metadata relating to the purchase of a batch of tags.
    """

    order_number = models.CharField(max_length=64)
    order_date = models.DateField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    tag_prefix = models.CharField(max_length=16, blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    paid_by = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    source = models.CharField(
        max_length=256,
        choices=SOURCE_CHOICES,
        default="direct",
        db_index=True,
    )
    source_id = models.CharField(
        max_length=256,
        db_index=True,
        default="na",
        help_text="The ID of this record in the original source (if applicable)",
    )

    def __str__(self):
        return self.order_number


class TurtleTag(models.Model):
    """Metadata related to a given turtle tag.
    """

    SIDE_CHOICES = (
        ("left", "Left"),
        ("right", "Right"),
    )
    TAG_TYPE_CHOICES = (
        ("flipper-tag", "Flipper tag"),
        ("pit-tag", "Pit tag"),
    )

    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    entered_by = models.ForeignKey(User, models.PROTECT, related_name="entered_by", blank=True, null=True)
    serial = models.CharField(max_length=64, unique=True)
    tag_type = models.CharField(max_length=64, choices=TAG_TYPE_CHOICES)
    turtle = models.ForeignKey(Turtle, models.PROTECT, blank=True, null=True)
    order = models.ForeignKey(TagPurchaseOrder, on_delete=models.PROTECT, blank=True, null=True)
    custodian = models.ForeignKey(
        User,
        models.PROTECT,
        blank=True,
        null=True,
        related_name="custodian",
        help_text="The person who has custodianship of the tag prior to application",
    )
    field_handler = models.ForeignKey(
        User,
        models.PROTECT,
        blank=True,
        null=True,
        help_text="The person who handled/applied the tag in the field",
    )
    side = models.CharField(
        max_length=64,
        choices=SIDE_CHOICES,
        blank=True,
        null=True,
        help_text="The side of the turtle where the tag was applied",
    )
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.CharField(max_length=128, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    batch_number = models.CharField(max_length=128, blank=True, null=True)
    box_number = models.CharField(max_length=128, blank=True, null=True)
    source = models.CharField(
        max_length=256,
        choices=SOURCE_CHOICES,
        default="direct",
        db_index=True,
    )
    source_id = models.CharField(
        max_length=256,
        db_index=True,
        default="na",
        help_text="The ID of this record in the original source (if applicable)",
    )

    def __str__(self):
        return self.serial

    def get_observations(self):
        """Return the queryset of TagObservation records for this tag.
        """
        return TagObservation.objects.filter(tag_type=self.tag_type, name=self.serial)
