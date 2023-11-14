
from django.contrib.gis.db import models

def incident_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/incident_<id>_attachents/<filename>
    return 'incident_{0}_attachents/{1}'.format(instance.incident.id, filename)

class Incident(models.Model):
    file_number = models.CharField(max_length=100)
    incident_date = models.DateTimeField()
    species = models.ForeignKey(
        'Species',
        on_delete=models.PROTECT)
    location_name = models.CharField(max_length=100)
    geo_location = models.PointField(null=True, blank=True)
    number_of_animals = models.IntegerField()
    mass_incident = models.BooleanField()
    incident_type = models.CharField(max_length=100)
    MALE = 'Male'
    FEMALE = 'Female'
    UNKNOWN = 'Unknown'

    SEX_CHOICES = [
        (MALE,'Male'),
        (FEMALE,'Female'),
        (UNKNOWN,'Unknown')
    ]
    sex = models.CharField(max_length=7, choices=SEX_CHOICES)

    ADULT = 'Adult'
    JUVENILE = 'Juvenile'
    SUBADULT = 'Sub-adult'
    CALF = 'Calf'
    NEONATE = 'Neonate'
    UNKNOWN = 'Unknown'

    AGE_CLASS_CHOICES = [
        (ADULT,'Adult'),
        (JUVENILE,'Juvenile'),
        (SUBADULT,'Sub-adult'),
        (CALF,'Calf'),
        (NEONATE,'Neonate'),
        (UNKNOWN,'Unknown')
    ]
    age_class = models.CharField(max_length=10,choices=AGE_CLASS_CHOICES)

    length = models.DecimalField(max_digits=3,decimal_places=2,help_text="in meters")

    weight = models.DecimalField(max_digits=6,decimal_places=2,help_text="in kilograms")

    comments = models.TextField(blank=True)

    photos_taken = models.BooleanField()

    samples_taken = models.BooleanField()

    post_mortem = models.BooleanField()

    carcass_location_fate = models.CharField(blank=True,max_length=100,help_text='Carcass transported to or disposed of site')

    entanglement_gear = models.CharField(max_length=50,blank=True) #choices

    DBCA_staff_attended = models.BooleanField()

    CONDITION_FOUND_CHOICES = [
        ('Alive','Alive'),
        ('Dead','Dead')
    ]
    condition_when_found = models.CharField(max_length=5,choices=CONDITION_FOUND_CHOICES)

    outcome = models.CharField(max_length=100) #choices

    cause_of_death = models.CharField(max_length=100,blank=True) #choices

    # @property
    # def latitude(self):
    #     """Return the WGS 84 DD latitude."""
    #     if self.geo_location:
    #         return self.geo_location.y
    #     return None

    # @property
    # def longitude(self):
    #     """Return the WGS 84 DD longitude."""
    #     if self.geo_location:
    #         return self.geo_location.x
    #     return None

class Uploaded_file(models.Model):  
    incident = models.ForeignKey(Incident,on_delete=models.CASCADE)
    title = models.CharField(
        max_length=100,
        verbose_name="Attachment name"
    )
    file = models.FileField(upload_to=incident_directory_path)

    def __str__(self):
        return f"Media {self.pk}: {self.title}"


class Species(models.Model):
    common_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "species"
    
    def __str__(self):
        return f"{self.scientific_name} ({self.common_name})"
