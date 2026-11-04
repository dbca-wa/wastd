from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import DatabaseError, models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Organisation(models.Model):
    """An Organisation owns records and has Users.

    * Organisations run Campaigns, which create Encounters and Surveys, which are owned by the Organisation.
    * Users belong to a set of Organisations.
    * The relationship of Users and Records (Enc, Surv) to Organsations can be used to manage data visibility and access.
    """

    code = models.SlugField(
        max_length=500,
        unique=True,
        verbose_name="Code",
        help_text="A unique, url-safe code.",
    )

    label = models.CharField(
        blank=True,
        null=True,
        max_length=500,
        verbose_name="Label",
        help_text="A human-readable, self-explanatory label.",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="A comprehensive description.",
    )

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return self.label

class OrganisationExportAssignment(models.Model):
    """Defines which WAMTRAM location data an Organisation may export."""

    class ValidityType(models.TextChoices):
        PERMANENT = "permanent", "Permanent"
        TIME_LIMITED = "time_limited", "Time limited"

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="export_assignments",
    )

    # References WAMTRAM2 TRT_LOCATIONS.LOCATION_CODE.
    # This is deliberately not a ForeignKey because TRT_LOCATIONS
    # is an unmanaged table in the SQL Server database.
    location_code = models.CharField(
        max_length=2,
        verbose_name="Location",
    )

    # Data period available to this Organisation at this location.
    data_from = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data from",
    )
    data_to = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data to",
    )

    validity_type = models.CharField(
        max_length=20,
        choices=ValidityType.choices,
        default=ValidityType.TIME_LIMITED,
        verbose_name="Export validity",
    )
    valid_from = models.DateField(
        blank=True,
        null=True,
        verbose_name="Valid from",
    )
    valid_to = models.DateField(
        blank=True,
        null=True,
        verbose_name="Valid to",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("organisation", "location_code", "data_from")
        verbose_name = "Organisation export assignment"
        verbose_name_plural = "Organisation export assignments"

    def clean(self):
        errors = {}

        if (
            self.data_from
            and self.data_to
            and self.data_from > self.data_to
        ):
            errors["data_to"] = (
                "Data to must be on or after Data from."
            )

        if self.validity_type == self.ValidityType.TIME_LIMITED:
            if not self.valid_from:
                errors["valid_from"] = (
                    "Valid from is required for time-limited access."
                )

            if not self.valid_to:
                errors["valid_to"] = (
                    "Valid to is required for time-limited access."
                )

            if (
                self.valid_from
                and self.valid_to
                and self.valid_from > self.valid_to
            ):
                errors["valid_to"] = (
                    "Valid to must be on or after Valid from."
                )

        elif self.validity_type == self.ValidityType.PERMANENT:
            if self.valid_from or self.valid_to:
                errors["validity_type"] = (
                    "Permanent access must not have validity dates."
                )

        if errors:
            raise ValidationError(errors)

    @classmethod
    def currently_valid_for_organisations(cls, organisations):
        today = timezone.localdate()

        return cls.objects.filter(
            organisation__in=organisations
        ).filter(
            models.Q(validity_type=cls.ValidityType.PERMANENT)
            | models.Q(
                validity_type=cls.ValidityType.TIME_LIMITED,
                valid_from__lte=today,
                valid_to__gte=today,
            )
        )

    @property
    def current_status(self):
        if self.validity_type == self.ValidityType.PERMANENT:
            return "Permanent"

        today = timezone.localdate()

        if self.valid_from and today < self.valid_from:
            return "Not started"

        if self.valid_to and today > self.valid_to:
            return "Expired"

        if self.valid_from and self.valid_to:
            return "Active"

        return "Invalid"

    def __str__(self):
        return f"{self.organisation} - {self.location_code}"

class User(AbstractUser):
    """Customised User class."""

    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField("Name of User", blank=True, max_length=255)
    nickname = models.CharField("Preferred name", blank=True, max_length=255)
    aliases = models.TextField(
        "Aliases of User",
        blank=True,
        help_text="Any names this user is known as in other databases and data collection forms. Separate names by comma.",
    )
    role = models.TextField("Role of User", blank=True, null=True, help_text="The role of the user.")
    affiliation = models.TextField(
        "Affiliation",
        blank=True,
        help_text="The organisational affiliation of the user as free text.",
    )
    organisations = models.ManyToManyField(
        Organisation,
        related_name="members",
        blank=True,
        help_text="The organisational affiliation is used to control data visibility and access. A user can be a member of several Organisations.",
    )
    phone = PhoneNumberField(
        verbose_name="Phone Number",
        blank=True,
        null=True,
        help_text="The primary contact number including national prefix, e.g. +61 412 345 678. Spaces are accepted but will be removed on saving.",
    )
    alive = models.BooleanField(
        verbose_name="Alive",
        default=True,
        help_text="Deceased users should not be attempted to be contacted.",
    )
    can_access_tracks_nests = models.BooleanField(
    "Tracks and Nests module access",
    default=False,
    )

    can_access_tagging = models.BooleanField(
        "Turtle Tagging module access",
        default=False,
    )

    can_access_marine_wildlife = models.BooleanField(
        "Marine Wildlife module access",
        default=False,
    )

    class Meta:
        ordering = ["name", "username"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        if self.is_active:
            return f"{self.name} ({self.pk})" if self.name else self.email
        else:
            return f"{self.name} ({self.pk}) [INACTIVE]" if self.name else f"{self.email} ({self.pk}) [INACTIVE]"

    def save(self, *args, **kwargs):
        if not self.password:
            self.set_unusable_password()
        if not self.date_joined:
            self.date_joined = timezone.now()
        super(User, self).save(*args, **kwargs)

    def card_template(self):
        return "users/user_card.html"

    def fullname(self):
        """The full name plus email."""
        return "{} ({})".format(self.name or self.username, self.role)

    @staticmethod
    def autocomplete_search_fields():
        """Search fields for Grappelli admin skin."""
        return (
            "id__iexact",
            "name__icontains",
            "role__icontains",
            "aliases__icontains",
            "affiliation__icontains",
        )
    def has_module_access(self, module):
        if not self.is_authenticated:
            return False

        if self.is_staff or self.is_superuser:
            return True

        return {
            "tracks_nests": self.can_access_tracks_nests,
            "tagging": self.can_access_tagging,
            "marine_wildlife": self.can_access_marine_wildlife,
        }.get(module, False)
    # -------------------------------------------------------------------------
    # URLs
    # Override create and update until we have front end forms
    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse("admin:{}_{}_add".format(cls._meta.app_label, cls._meta.model_name))

    @property
    def update_url(self):
        """Update url. Redirects to admin update URL, as we don't have a front end form yet."""
        return self.absolute_admin_url

    @property
    def absolute_admin_url(self):
        """Return the absolute admin change URL.

        Default: admin:app_model_change(**pk)
        """
        return reverse(
            "admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name),
            args=[self.pk],
        )

    def get_absolute_url(self):
        """Detail url, used by Django to link admin to site.

        Default: app:model-detail(**pk).
        """
        return reverse(
            "{}:{}-detail".format(self._meta.app_label, self._meta.model_name),
            kwargs={"pk": self.pk},
        )

    @classmethod
    def list_url(cls):
        return reverse("{}:{}-list".format(cls._meta.app_label, cls._meta.model_name))


class AuditLog(models.Model):
    """Minimal server-side audit trail for destructive actions."""

    ACTION_DELETE = "DELETE"

    action = models.CharField(max_length=20, db_index=True)
    app_label = models.CharField(max_length=100, db_index=True)
    model_name = models.CharField(max_length=100, db_index=True)
    object_pk = models.TextField(blank=True)
    object_repr = models.TextField(blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    path = models.TextField(blank=True)
    method = models.CharField(max_length=10, blank=True)
    remote_addr = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Audit log"
        verbose_name_plural = "Audit logs"

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.action} {self.app_label}.{self.model_name} {self.object_pk}"


@receiver(pre_delete)
def log_model_delete(sender, instance, **kwargs):
    if sender is AuditLog:
        return
    if sender._meta.app_label == "sessions" and sender._meta.model_name == "session":
        return
    request = None
    try:
        from .middleware import get_current_audit_request

        request = get_current_audit_request()
    except Exception:
        request = None

    actor = None
    if request and getattr(request, "user", None) and request.user.is_authenticated:
        actor = request.user

    try:
        AuditLog.objects.create(
            action=AuditLog.ACTION_DELETE,
            app_label=instance._meta.app_label,
            model_name=instance._meta.model_name,
            object_pk=str(instance.pk or ""),
            object_repr=str(instance),
            actor=actor,
            path=request.get_full_path() if request else "",
            method=request.method if request else "",
            remote_addr=_get_remote_addr(request),
        )
    except DatabaseError:
        # Do not block the actual delete if the audit table has not been migrated yet.
        return


def _get_remote_addr(request):
    if not request:
        return None
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
