from django.contrib.gis.db import models


def incident_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/incident_<id>_attachents/<filename>
    return 'incident_{0}_attachents/{1}'.format(instance.incident.id, filename)


class Incident(models.Model):
    #file_number = models.CharField(max_length=100)
    incident_date = models.DateField()
    incident_time = models.TimeField(null=True,blank=True)
    species = models.ForeignKey(
        'Species',
        on_delete=models.PROTECT)
    species_confirmed_genetically = models.BooleanField(default=False)
    location_name = models.CharField(max_length=100,null=True,blank=True)
    geo_location = models.PointField(null=True, blank=True)
    number_of_animals = models.IntegerField()
    mass_incident = models.BooleanField(default=False)

    STRANDING = 'Stranding'
    ENTANGLEMENT = 'Entanglement'
    ENTRAPMENT = 'Entrapment'
    VESSEL_COLLISION = 'Vessel collision'
    UNUSUAL_MORTALITY_EVENT = 'Unusual mortality event'
    HAULED_OUT = 'Hauled-out'
    INCIDENT_TYPE_CHOICES = [
        (STRANDING, 'Stranding'),
        (ENTANGLEMENT, 'Entanglement'),
        (ENTRAPMENT, 'Entrapment'),
        (VESSEL_COLLISION, 'Vessel collision'),
        (UNUSUAL_MORTALITY_EVENT, 'Unusual mortality event'),
        (HAULED_OUT, 'Hauled-out (for pinnipeds)')
        
    ]
    incident_type = models.CharField(max_length=50,choices=INCIDENT_TYPE_CHOICES)

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
    NEWBORN = 'Newborn'
    UNKNOWN = 'Unknown'
    PUP = 'Pup'
    AGE_CLASS_CHOICES = [
        (ADULT,'Adult'),
        (JUVENILE,'Juvenile'),
        (SUBADULT,'Sub-adult'),
        (CALF,'Calf'),
        (NEWBORN,'Newborn'),
        (PUP,'Pup'),
        (UNKNOWN,'Unknown')
    ]
    age_class = models.CharField(max_length=10,choices=AGE_CLASS_CHOICES)

    length = models.DecimalField(max_digits=10,decimal_places=2,help_text="in centimeters",null=True,blank=True)

    weight = models.DecimalField(max_digits=10,decimal_places=2,help_text="in kilograms",null=True,blank=True)
    weight_is_estimated = models.BooleanField(default=False)

    carcass_location_fate = models.CharField(blank=True,max_length=500,help_text='Carcass transported to or disposed of site')

    ENTANGLEMENT_GEAR_CHOICES = [
        ('Fishing net','Fishing net'),
        ('Rock lobster pot/rope','Rock lobster pot/rope'),
        ('Crab pot/rope','Crab pot/rope'),
        ('Unknown origin set gear (pot/rope)','Unknown origin set gear (pot/rope)'),
        ('Rope','Rope'),
        ('Monofilament fishing line','Monofilament fishing line'),
        ('Professional longline','Professional longline'),
        ('Braided line','Braided line'),
        ('Aquaculture infrastructure','Aquaculture infrastructure'),
        ('Tackle','Tackle'),
        ('Plastic debris','Plastic debris'),
        ('Octopus gear','Octopus gear'),
        ('Other','Other'),
        ('Other (see comments)','Other (add in comments)')
    ]
    entanglement_gear = models.CharField(max_length=50, blank=True, choices=ENTANGLEMENT_GEAR_CHOICES)

    DBCA_staff_attended = models.BooleanField(default=False)

    CONDITION_FOUND_CHOICES = [
        ('Stage 1 = alive','Stage 1 = alive'),
        ('Stage 2 = fresh dead','Stage 2 = fresh dead'),
        ('Stage 3 = mild decomposition','Stage 3 = mild decomposition'),
        ('Stage 4 = advanced decomposition', 'Stage 4 = advanced decomposition'),
        ('Stage 5 = mummified/skeletal','Stage 5 = mummified/skeletal'),
        ('Unknown','Unknown')
    ]
    condition_when_found = models.CharField(max_length=40,choices=CONDITION_FOUND_CHOICES)

    OUTCOME_CHOICES = [
        ('Euthanased','Euthanased'),
        ('Restranded and euthanased','Restranded and euthanased'),
        ('Refloated, fate unknown','Refloated, fate unknown'),
        ('Died','Died'),
        ('Recovered','Recovered'),
        ('Released','Released'),
        ('Alive','Alive'),
        ('Unknown','Unknown')
    ]
    outcome = models.CharField(max_length=30, choices=OUTCOME_CHOICES)

    cause_of_death = models.CharField(max_length=500, blank=True)
    photos_taken = models.BooleanField(default=False)

    samples_taken = models.BooleanField(default=False)

    post_mortem = models.BooleanField(default=False)
    comments = models.TextField(blank=True)


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
