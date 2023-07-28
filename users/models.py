from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.authtoken.models import Token


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
        """The full name."""
        return self.label


class User(AbstractUser):
    """Customised User class.
    """

    # First Name and Last Name do not cover name patterns around the globe.
    name = models.CharField("Name of User", blank=True, max_length=255)
    nickname = models.CharField("Preferred name", blank=True, max_length=255)
    aliases = models.TextField(
        "Aliases of User",
        blank=True,
        help_text="Any names this user is known as in other databases and data collection forms. Separate names by comma.",
    )
    role = models.TextField(
        "Role of User", blank=True, null=True, help_text="The role of the user."
    )

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
        return "{0} ({1})".format(self.name or self.username, self.role)

    @property
    def apitoken(self):
        """The API token."""
        return Token.objects.get_or_create(user=self)[0].key

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

    # -------------------------------------------------------------------------
    # URLs
    # Override create and update until we have front end forms
    @classmethod
    def create_url(cls):
        """Create url. Default: app:model-create."""
        return reverse(
            "admin:{0}_{1}_add".format(cls._meta.app_label, cls._meta.model_name)
        )

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
            "admin:{0}_{1}_change".format(self._meta.app_label, self._meta.model_name),
            args=[self.pk],
        )

    def get_absolute_url(self):
        """Detail url, used by Django to link admin to site.

        Default: app:model-detail(**pk).
        """
        return reverse(
            "{0}:{1}-detail".format(self._meta.app_label, self._meta.model_name),
            kwargs={"pk": self.pk},
        )

    @classmethod
    def list_url(cls):
        """List url property. Default: app:model-list."""
        return reverse("{0}:{1}-list".format(cls._meta.app_label, cls._meta.model_name))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Create API auth token on User create.
    """
    if created:
        Token.objects.create(user=instance)
