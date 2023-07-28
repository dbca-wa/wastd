# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
# NOTE: don't add ordering for any model Meta - it breaks the DB connection.
from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import models
from django.urls import reverse


class TrtPersons(models.Model):
    person_id = models.AutoField(db_column='PERSON_ID', primary_key=True)
    first_name = models.CharField(db_column='FIRST_NAME', max_length=50)
    middle_name = models.CharField(db_column='MIDDLE_NAME', max_length=50, blank=True, null=True)
    surname = models.CharField(db_column='SURNAME', max_length=50, blank=True, null=True)
    specialty = models.CharField(db_column='SPECIALTY', max_length=255, blank=True, null=True)
    address_line_1 = models.CharField(db_column='ADDRESS_LINE_1', max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(db_column='ADDRESS_LINE_2', max_length=255, blank=True, null=True)
    town = models.CharField(db_column='TOWN', max_length=50, blank=True, null=True)
    state = models.CharField(db_column='STATE', max_length=10, blank=True, null=True)
    post_code = models.CharField(db_column='POST_CODE', max_length=10, blank=True, null=True)
    country = models.CharField(db_column='COUNTRY', max_length=50, blank=True, null=True)
    telephone = models.CharField(db_column='TELEPHONE', max_length=20, blank=True, null=True)
    fax = models.CharField(db_column='FAX', max_length=20, blank=True, null=True)
    mobile = models.CharField(db_column='MOBILE', max_length=20, blank=True, null=True)
    email = models.CharField(db_column='EMAIL', max_length=150, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=400, blank=True, null=True)
    transfer = models.CharField(db_column='Transfer', max_length=50, blank=True, null=True)
    recorder = models.BooleanField(db_column='Recorder')

    class Meta:
        managed = False
        db_table = 'TRT_PERSONS'

    def __str__(self):
        return f"{self.person_id} {self.first_name} {self.surname}"

    def get_name(self):
        return f"{self.first_name} {self.surname}".strip()


class TrtLocations(models.Model):
    location_code = models.CharField(db_column='LOCATION_CODE', primary_key=True, max_length=2)
    location_name = models.CharField(db_column='LOCATION_NAME', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_LOCATIONS'

    def __str__(self):
        return f"{self.location_code} - {self.location_name}"


class TrtPlaces(models.Model):
    place_code = models.CharField(db_column='PLACE_CODE', primary_key=True, max_length=4)
    place_name = models.CharField(db_column='PLACE_NAME', max_length=50, blank=True, null=True)
    location_code = models.ForeignKey(TrtLocations, models.DO_NOTHING, db_column='LOCATION_CODE', related_name='places')
    rookery = models.CharField(db_column='ROOKERY', max_length=1, blank=True, null=True)
    beach_approach = models.CharField(db_column='BEACH_APPROACH', max_length=50, blank=True, null=True)
    aspect = models.CharField(db_column='ASPECT', max_length=3, blank=True, null=True)
    datum_code = models.CharField(db_column='DATUM_CODE', max_length=5, blank=True, null=True)
    latitude = models.FloatField(db_column='LATITUDE', blank=True, null=True)
    longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_PLACES'

    def __str__(self):
        if self.place_name:
            return f"{self.place_code} - {self.place_name}"
        else:
            return f"{self.place_code}"

    def get_point(self):
        """Returns a geometry point as WGS84.
        """
        if not self.longitude or not self.latitude:
            return None
        if self.datum_code:
            if self.datum_code == "AGD66":
                datum = 4202
            elif self.datum_code == "AGD66":
                datum = 4203
            elif self.datum_code == "GDA94":
                datum = 4283
            elif self.datum_code == "WGS84":
                datum = 4326
        else:
            datum = 4326
        geom = Point(x=self.longitude, y=self.latitude, srid=datum)
        geom.transform(4326)
        return geom


class TrtBeachPositions(models.Model):
    beach_position_code = models.CharField(db_column='BEACH_POSITION_CODE', primary_key=True, max_length=2)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    new_code = models.CharField(db_column='New_Code', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_BEACH_POSITIONS'


class TrtBodyParts(models.Model):
    body_part = models.CharField(db_column='BODY_PART', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    flipper = models.BooleanField(db_column='FLIPPER')

    class Meta:
        managed = False
        db_table = 'TRT_BODY_PARTS'


class TrtCauseOfDeath(models.Model):
    cause_of_death = models.CharField(db_column='CAUSE_OF_DEATH', primary_key=True, max_length=2)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_CAUSE_OF_DEATH'


class TrtConditionCodes(models.Model):
    condition_code = models.CharField(db_column='CONDITION_CODE', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_CONDITION_CODES'


class TrtDamageCodes(models.Model):
    damage_code = models.CharField(db_column='DAMAGE_CODE', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    flipper = models.BooleanField(db_column='FLIPPER')

    class Meta:
        managed = False
        db_table = 'TRT_DAMAGE_CODES'


class TrtDamageCauseCodes(models.Model):
    damage_cause_code = models.CharField(db_column='DAMAGE_CAUSE_CODE', primary_key=True, max_length=2)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_DAMAGE_CAUSE_CODES'


class TrtDamageCause(models.Model):
    observation_id = models.IntegerField(db_column='OBSERVATION_ID')
    body_part = models.CharField(db_column='BODY_PART', max_length=1)
    damage_code = models.CharField(db_column='DAMAGE_CODE', max_length=1)
    damage_cause_code = models.CharField(db_column='DAMAGE_CAUSE_CODE', max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DAMAGE_CAUSE'


class TrtDataChanged(models.Model):
    trt_data_changed_id = models.AutoField(db_column='TRT_DATA_CHANGED_ID', primary_key=True)
    datachanged_date = models.DateTimeField(db_column='DATACHANGED_DATE', blank=True, null=True)
    datachangedby = models.CharField(db_column='DATACHANGEDBY', max_length=255, blank=True, null=True)
    comment = models.CharField(db_column='COMMENT', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DATA_CHANGED'


class TrtEntryBatches(models.Model):
    entry_batch_id = models.AutoField(db_column='ENTRY_BATCH_ID', primary_key=True)
    entry_date = models.DateTimeField(db_column='ENTRY_DATE', blank=True, null=True)
    entered_person_id = models.IntegerField(db_column='ENTERED_PERSON_ID', blank=True, null=True)
    filename = models.CharField(db_column='FILENAME', max_length=255, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    pr_date_convention = models.BooleanField(db_column='PR_DATE_CONVENTION')

    class Meta:
        managed = False
        db_table = 'TRT_ENTRY_BATCHES'


class TrtDataEntry(models.Model):
    data_entry_id = models.AutoField(db_column='DATA_ENTRY_ID', primary_key=True)
    entry_batch = models.ForeignKey(TrtEntryBatches, models.DO_NOTHING, db_column='ENTRY_BATCH_ID')
    user_entry_id = models.IntegerField(db_column='USER_ENTRY_ID')
    turtle_id = models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)
    do_not_process = models.BooleanField(db_column='DO_NOT_PROCESS')
    recapture_left_tag_id = models.CharField(db_column='RECAPTURE_LEFT_TAG_ID', max_length=10, blank=True, null=True)
    recapture_left_tag_id_2 = models.CharField(db_column='RECAPTURE_LEFT_TAG_ID_2', max_length=10, blank=True, null=True)
    recapture_right_tag_id = models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID', max_length=10, blank=True, null=True)
    recapture_right_tag_id_2 = models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID_2', max_length=10, blank=True, null=True)
    recapture_pit_tag_id = models.CharField(db_column='RECAPTURE_PIT_TAG_ID', max_length=50, blank=True, null=True)
    other_left_tag = models.CharField(db_column='OTHER_LEFT_TAG', max_length=2, blank=True, null=True)
    other_right_tag = models.CharField(db_column='OTHER_RIGHT_TAG', max_length=2, blank=True, null=True)
    new_left_tag_id = models.CharField(db_column='NEW_LEFT_TAG_ID', max_length=10, blank=True, null=True)
    new_left_tag_id_2 = models.CharField(db_column='NEW_LEFT_TAG_ID_2', max_length=10, blank=True, null=True)
    new_right_tag_id = models.CharField(db_column='NEW_RIGHT_TAG_ID', max_length=10, blank=True, null=True)
    new_right_tag_id_2 = models.CharField(db_column='NEW_RIGHT_TAG_ID_2', max_length=10, blank=True, null=True)
    new_pit_tag_id = models.CharField(db_column='NEW_PIT_TAG_ID', max_length=50, blank=True, null=True)
    alive = models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)
    place_code = models.CharField(db_column='PLACE_CODE', max_length=4, blank=True, null=True)
    observation_date = models.DateTimeField(db_column='OBSERVATION_DATE', blank=True, null=True)
    observation_time = models.DateTimeField(db_column='OBSERVATION_TIME', blank=True, null=True)
    nesting = models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)
    species_code = models.CharField(db_column='SPECIES_CODE', max_length=2, blank=True, null=True)
    identification_confidence = models.CharField(db_column='IDENTIFICATION_CONFIDENCE', max_length=1, blank=True, null=True)
    sex = models.CharField(db_column='SEX', max_length=1, blank=True, null=True)
    curved_carapace_length = models.IntegerField(db_column='CURVED_CARAPACE_LENGTH', blank=True, null=True)
    curved_carapace_width = models.IntegerField(db_column='CURVED_CARAPACE_WIDTH', blank=True, null=True)
    activity_code = models.CharField(db_column='ACTIVITY_CODE', max_length=1, blank=True, null=True)
    beach_position_code = models.CharField(db_column='BEACH_POSITION_CODE', max_length=2, blank=True, null=True)
    damage_carapace = models.CharField(db_column='DAMAGE_CARAPACE', max_length=1, blank=True, null=True)
    damage_lff = models.CharField(db_column='DAMAGE_LFF', max_length=1, blank=True, null=True)
    damage_rff = models.CharField(db_column='DAMAGE_RFF', max_length=1, blank=True, null=True)
    damage_lhf = models.CharField(db_column='DAMAGE_LHF', max_length=1, blank=True, null=True)
    damage_rhf = models.CharField(db_column='DAMAGE_RHF', max_length=1, blank=True, null=True)
    body_part_1 = models.CharField(db_column='BODY_PART_1', max_length=1, blank=True, null=True)
    damage_code_1 = models.CharField(db_column='DAMAGE_CODE_1', max_length=1, blank=True, null=True)
    body_part_2 = models.CharField(db_column='BODY_PART_2', max_length=1, blank=True, null=True)
    damage_code_2 = models.CharField(db_column='DAMAGE_CODE_2', max_length=1, blank=True, null=True)
    egg_count = models.IntegerField(db_column='EGG_COUNT', blank=True, null=True)
    egg_count_method = models.CharField(db_column='EGG_COUNT_METHOD', max_length=3, blank=True, null=True)
    clutch_completed = models.CharField(db_column='CLUTCH_COMPLETED', max_length=1, blank=True, null=True)
    measured_by = models.CharField(db_column='MEASURED_BY', max_length=50, blank=True, null=True)
    recorded_by = models.CharField(db_column='RECORDED_BY', max_length=50, blank=True, null=True)
    tagged_by = models.CharField(db_column='TAGGED_BY', max_length=50, blank=True, null=True)
    entered_by = models.CharField(db_column='ENTERED_BY', max_length=50, blank=True, null=True)
    measured_recorded_by = models.CharField(db_column='MEASURED_RECORDED_BY', max_length=50, blank=True, null=True)
    measurement_type_1 = models.CharField(db_column='MEASUREMENT_TYPE_1', max_length=10, blank=True, null=True)
    measurement_value_1 = models.FloatField(db_column='MEASUREMENT_VALUE_1', blank=True, null=True)
    measurement_type_2 = models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)
    measurement_value_2 = models.FloatField(db_column='MEASUREMENT_VALUE_2', blank=True, null=True)
    datum_code = models.CharField(db_column='DATUM_CODE', max_length=5, blank=True, null=True)
    zone = models.IntegerField(db_column='ZONE', blank=True, null=True)
    easting = models.FloatField(db_column='EASTING', blank=True, null=True)
    northing = models.FloatField(db_column='NORTHING', blank=True, null=True)
    latitude = models.FloatField(db_column='LATITUDE', blank=True, null=True)
    longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)
    latitude_degrees = models.IntegerField(db_column='LATITUDE_DEGREES', blank=True, null=True)
    latitude_minutes = models.FloatField(db_column='LATITUDE_MINUTES', blank=True, null=True)
    latitude_seconds = models.FloatField(db_column='LATITUDE_SECONDS', blank=True, null=True)
    longitude_degrees = models.IntegerField(db_column='LONGITUDE_DEGREES', blank=True, null=True)
    longitude_minutes = models.FloatField(db_column='LONGITUDE_MINUTES', blank=True, null=True)
    longitude_seconds = models.FloatField(db_column='LONGITUDE_SECONDS', blank=True, null=True)
    identification_type = models.CharField(db_column='IDENTIFICATION_TYPE', max_length=10, blank=True, null=True)
    identifier = models.CharField(db_column='IDENTIFIER', max_length=20, blank=True, null=True)
    comment_fromrecordedtagstable = models.CharField(db_column='COMMENT_FROMRECORDEDTAGSTABLE', max_length=255, blank=True, null=True)
    scars_left = models.BooleanField(db_column='SCARS_LEFT')
    scars_right = models.BooleanField(db_column='SCARS_RIGHT')
    other_tags = models.CharField(db_column='OTHER_TAGS', max_length=255, blank=True, null=True)
    other_tags_identification_type = models.CharField(db_column='OTHER_TAGS_IDENTIFICATION_TYPE', max_length=10, blank=True, null=True)
    scars_left_scale_1 = models.BooleanField(db_column='SCARS_LEFT_SCALE_1')
    scars_left_scale_2 = models.BooleanField(db_column='SCARS_LEFT_SCALE_2')
    scars_left_scale_3 = models.BooleanField(db_column='SCARS_LEFT_SCALE_3')
    scars_right_scale_1 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_1')
    scars_right_scale_2 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_2')
    scars_right_scale_3 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_3')
    cc_length_not_measured = models.BooleanField(db_column='CC_LENGTH_NOT_MEASURED')
    cc_notch_length_not_measured = models.BooleanField(db_column='CC_NOTCH_LENGTH_NOT_MEASURED')
    cc_width_not_measured = models.BooleanField(db_column='CC_WIDTH_NOT_MEASURED')
    tagscarnotchecked = models.BooleanField(db_column='TAGSCARNOTCHECKED')
    didnotcheckforinjury = models.BooleanField(db_column='DIDNOTCHECKFORINJURY')
    comments = models.TextField(db_column='COMMENTS', blank=True, null=True)
    error_number = models.IntegerField(db_column='ERROR_NUMBER', blank=True, null=True)
    error_message = models.CharField(db_column='ERROR_MESSAGE', max_length=255, blank=True, null=True)
    recapture_left_tag_id_3 = models.CharField(db_column='RECAPTURE_LEFT_TAG_ID_3', max_length=10, blank=True, null=True)
    recapture_right_tag_id_3 = models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID_3', max_length=10, blank=True, null=True)
    body_part_3 = models.CharField(db_column='BODY_PART_3', max_length=1, blank=True, null=True)
    damage_code_3 = models.CharField(db_column='DAMAGE_CODE_3', max_length=1, blank=True, null=True)
    tissue_type_1 = models.CharField(db_column='TISSUE_TYPE_1', max_length=5, blank=True, null=True)
    sample_label_1 = models.CharField(db_column='SAMPLE_LABEL_1', max_length=50, blank=True, null=True)
    tissue_type_2 = models.CharField(db_column='TISSUE_TYPE_2', max_length=5, blank=True, null=True)
    sample_label_2 = models.CharField(db_column='SAMPLE_LABEL_2', max_length=50, blank=True, null=True)
    turtle_comments = models.CharField(db_column='TURTLE_COMMENTS', max_length=255, blank=True, null=True)
    recapture_pit_tag_id_2 = models.CharField(db_column='RECAPTURE_PIT_TAG_ID_2', max_length=50, blank=True, null=True)
    new_pit_tag_id_2 = models.CharField(db_column='NEW_PIT_TAG_ID_2', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DATA_ENTRY'
        unique_together = (('entry_batch', 'user_entry_id'),)


class TrtDataEntryExceptions(models.Model):
    entry_batch_id = models.IntegerField(db_column='ENTRY_BATCH_ID', primary_key=True)
    data_entry_id = models.IntegerField(db_column='DATA_ENTRY_ID')
    turtle_id = models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)
    recapture_left_tag_id = models.CharField(db_column='RECAPTURE_LEFT_TAG_ID', max_length=10, blank=True, null=True)
    recapture_right_tag_id = models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID', max_length=10, blank=True, null=True)
    recapture_left_tag_id_2 = models.CharField(db_column='RECAPTURE_LEFT_TAG_ID_2', max_length=10, blank=True, null=True)
    recapture_right_tag_id_2 = models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID_2', max_length=10, blank=True, null=True)
    other_left_tag = models.CharField(db_column='OTHER_LEFT_TAG', max_length=2, blank=True, null=True)
    other_right_tag = models.CharField(db_column='OTHER_RIGHT_TAG', max_length=2, blank=True, null=True)
    new_left_tag_id = models.CharField(db_column='NEW_LEFT_TAG_ID', max_length=10, blank=True, null=True)
    new_right_tag_id = models.CharField(db_column='NEW_RIGHT_TAG_ID', max_length=10, blank=True, null=True)
    alive = models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)
    place_code = models.CharField(db_column='PLACE_CODE', max_length=4, blank=True, null=True)
    observation_date = models.DateTimeField(db_column='OBSERVATION_DATE', blank=True, null=True)
    observation_time = models.DateTimeField(db_column='OBSERVATION_TIME', blank=True, null=True)
    nesting = models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)
    species_code = models.CharField(db_column='SPECIES_CODE', max_length=2, blank=True, null=True)
    identification_confidence = models.CharField(db_column='IDENTIFICATION_CONFIDENCE', max_length=1, blank=True, null=True)
    sex = models.CharField(db_column='SEX', max_length=1, blank=True, null=True)
    curved_carapace_length = models.IntegerField(db_column='CURVED_CARAPACE_LENGTH', blank=True, null=True)
    curved_carapace_width = models.IntegerField(db_column='CURVED_CARAPACE_WIDTH', blank=True, null=True)
    activity_code = models.CharField(db_column='ACTIVITY_CODE', max_length=1, blank=True, null=True)
    beach_position_code = models.CharField(db_column='BEACH_POSITION_CODE', max_length=2, blank=True, null=True)
    damage_carapace = models.CharField(db_column='DAMAGE_CARAPACE', max_length=1, blank=True, null=True)
    damage_lff = models.CharField(db_column='DAMAGE_LFF', max_length=1, blank=True, null=True)
    damage_rff = models.CharField(db_column='DAMAGE_RFF', max_length=1, blank=True, null=True)
    damage_lhf = models.CharField(db_column='DAMAGE_LHF', max_length=1, blank=True, null=True)
    damage_rhf = models.CharField(db_column='DAMAGE_RHF', max_length=1, blank=True, null=True)
    clutch_completed = models.CharField(db_column='CLUTCH_COMPLETED', max_length=1, blank=True, null=True)
    egg_count = models.IntegerField(db_column='EGG_COUNT', blank=True, null=True)
    egg_count_method = models.CharField(db_column='EGG_COUNT_METHOD', max_length=3, blank=True, null=True)
    measured_by = models.CharField(db_column='MEASURED_BY', max_length=50, blank=True, null=True)
    recorded_by = models.CharField(db_column='RECORDED_BY', max_length=50, blank=True, null=True)
    tagged_by = models.CharField(db_column='TAGGED_BY', max_length=50, blank=True, null=True)
    measurement_type_1 = models.CharField(db_column='MEASUREMENT_TYPE_1', max_length=10, blank=True, null=True)
    measurement_value_1 = models.FloatField(db_column='MEASUREMENT_VALUE_1', blank=True, null=True)
    measurement_type_2 = models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)
    measurement_value_2 = models.FloatField(db_column='MEASUREMENT_VALUE_2', blank=True, null=True)
    datum_code = models.CharField(db_column='DATUM_CODE', max_length=5, blank=True, null=True)
    latitude = models.FloatField(db_column='LATITUDE', blank=True, null=True)
    longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)
    latitude_degrees = models.IntegerField(db_column='LATITUDE_DEGREES', blank=True, null=True)
    latitude_minutes = models.FloatField(db_column='LATITUDE_MINUTES', blank=True, null=True)
    latitude_seconds = models.FloatField(db_column='LATITUDE_SECONDS', blank=True, null=True)
    longitude_degrees = models.IntegerField(db_column='LONGITUDE_DEGREES', blank=True, null=True)
    longitude_minutes = models.FloatField(db_column='LONGITUDE_MINUTES', blank=True, null=True)
    longitude_seconds = models.FloatField(db_column='LONGITUDE_SECONDS', blank=True, null=True)
    zone = models.IntegerField(db_column='ZONE', blank=True, null=True)
    easting = models.FloatField(db_column='EASTING', blank=True, null=True)
    northing = models.FloatField(db_column='NORTHING', blank=True, null=True)
    identification_type = models.CharField(db_column='IDENTIFICATION_TYPE', max_length=10, blank=True, null=True)
    identifier = models.CharField(db_column='IDENTIFIER', max_length=20, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DATA_ENTRY_EXCEPTIONS'
        unique_together = (('entry_batch_id', 'data_entry_id'),)


class TrtDataEntryPersons(models.Model):
    data_entry_person_id = models.AutoField(db_column='DATA_ENTRY_PERSON_ID', primary_key=True)
    entry_batch = models.ForeignKey(TrtEntryBatches, models.DO_NOTHING, db_column='ENTRY_BATCH_ID')
    person_name = models.CharField(db_column='PERSON_NAME', max_length=100)
    person_id = models.IntegerField(db_column='PERSON_ID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DATA_ENTRY_PERSONS'
        unique_together = (('entry_batch', 'person_name'),)


class TrtDatumCodes(models.Model):
    datum_code = models.CharField(db_column='DATUM_CODE', primary_key=True, max_length=5)
    datum_description = models.CharField(db_column='DATUM_DESCRIPTION', max_length=50, blank=True, null=True)
    semi_major_axis = models.FloatField(db_column='SEMI_MAJOR_AXIS', blank=True, null=True)
    inverse_flattening = models.FloatField(db_column='INVERSE_FLATTENING', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DATUM_CODES'


class TrtDefault(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10)
    dataentry_exportpath = models.CharField(db_column='DataEntry_ExportPath', max_length=200)
    dataentry_sourcedatabase = models.CharField(db_column='DataEntry_SourceDatabase', max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DEFAULT'


class TrtDocuments(models.Model):
    document_id = models.AutoField(db_column='DOCUMENT_ID', primary_key=True)
    document_type = models.CharField(db_column='DOCUMENT_TYPE', max_length=10)
    filename = models.CharField(db_column='FILENAME', max_length=255, blank=True, null=True)
    turtle_id = models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)
    person_id = models.IntegerField(db_column='PERSON_ID', blank=True, null=True)
    species_code = models.CharField(db_column='SPECIES_CODE', max_length=2, blank=True, null=True)
    title = models.CharField(db_column='TITLE', max_length=255, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DOCUMENTS'


class TrtDocumentTypes(models.Model):
    document_type = models.CharField(db_column='DOCUMENT_TYPE', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_DOCUMENT_TYPES'


class TrtEggCountMethods(models.Model):
    egg_count_method = models.CharField(db_column='EGG_COUNT_METHOD', primary_key=True, max_length=3)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_EGG_COUNT_METHODS'


class TrtIdentificationTypes(models.Model):
    identification_type = models.CharField(db_column='IDENTIFICATION_TYPE', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_IDENTIFICATION_TYPES'


class TrtMeasurementTypes(models.Model):
    measurement_type = models.CharField(db_column='MEASUREMENT_TYPE', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=100)
    measurement_units = models.CharField(db_column='MEASUREMENT_UNITS', max_length=10, blank=True, null=True)
    minimum_value = models.FloatField(db_column='MINIMUM_VALUE', blank=True, null=True)
    maximum_value = models.FloatField(db_column='MAXIMUM_VALUE', blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_MEASUREMENT_TYPES'


class TrtNesting(models.Model):
    place_code = models.CharField(db_column='PLACE_CODE', primary_key=True, max_length=4)
    species_code = models.CharField(db_column='SPECIES_CODE', max_length=2)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_NESTING'
        unique_together = (('place_code', 'species_code'),)


class TrtNestingSeason(models.Model):
    nesting_seasonid = models.AutoField(db_column='NESTING_SEASONID', primary_key=True)
    nesting_season = models.CharField(db_column='NESTING_SEASON', max_length=20)
    startdate = models.DateTimeField(db_column='STARTDATE')
    enddate = models.DateTimeField(db_column='ENDDATE')

    class Meta:
        managed = False
        db_table = 'TRT_NESTING_SEASON'


class TrtSpecies(models.Model):
    species_code = models.CharField(db_column='SPECIES_CODE', primary_key=True, max_length=2)
    scientific_name = models.CharField(db_column='SCIENTIFIC_NAME', max_length=50, blank=True, null=True)
    common_name = models.CharField(db_column='COMMON_NAME', max_length=50, blank=True, null=True)
    old_species_code = models.CharField(db_column='OLD_SPECIES_CODE', max_length=2, blank=True, null=True)
    hide_dataentry = models.BooleanField(db_column='Hide_DataEntry')

    class Meta:
        managed = False
        db_table = 'TRT_SPECIES'


class TrtTurtleStatus(models.Model):
    turtle_status = models.CharField(db_column='TURTLE_STATUS', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=100)
    new_tag_list = models.BooleanField(db_column='NEW_TAG_LIST')

    class Meta:
        managed = False
        db_table = 'TRT_TURTLE_STATUS'


class TrtTurtles(models.Model):
    turtle_id = models.IntegerField(db_column='TURTLE_ID', primary_key=True)
    species_code = models.ForeignKey(TrtSpecies, models.DO_NOTHING, db_column='SPECIES_CODE')
    identification_confidence = models.CharField(db_column='IDENTIFICATION_CONFIDENCE', max_length=1, blank=True, null=True)
    sex = models.CharField(db_column='SEX', max_length=1)
    turtle_status = models.ForeignKey(TrtTurtleStatus, models.DO_NOTHING, db_column='TURTLE_STATUS', blank=True, null=True)
    location_code = models.ForeignKey(TrtLocations, models.DO_NOTHING, db_column='LOCATION_CODE', blank=True, null=True)
    cause_of_death = models.ForeignKey(TrtCauseOfDeath, models.DO_NOTHING, db_column='CAUSE_OF_DEATH', blank=True, null=True)
    re_entered_population = models.CharField(db_column='RE_ENTERED_POPULATION', max_length=1, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    entered_by = models.CharField(db_column='ENTERED_BY', max_length=50, blank=True, null=True)
    date_entered = models.DateTimeField(db_column='DATE_ENTERED', blank=True, null=True)
    original_turtle_id = models.IntegerField(db_column='ORIGINAL_TURTLE_ID', blank=True, null=True)
    entry_batch_id = models.IntegerField(db_column='ENTRY_BATCH_ID', blank=True, null=True)
    tag = models.CharField(db_column='Tag', max_length=255, blank=True, null=True)
    mund_id = models.CharField(db_column='Mund_ID', max_length=255, blank=True, null=True)
    turtle_name = models.CharField(db_column='TURTLE_NAME', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_TURTLES'

    def __str__(self):
        if self.turtle_name:
            return f'{self.turtle_id}: {self.species_code.common_name} ({self.sex}) - {self.turtle_name}'
        else:
            return f'{self.turtle_id}: {self.species_code.common_name} ({self.sex})'

    def get_absolute_url(self):
        return reverse('wamtram:turtle_detail', kwargs={'pk': self.pk})


class TrtIdentification(models.Model):
    turtle = models.OneToOneField(TrtTurtles, models.DO_NOTHING, db_column='TURTLE_ID', primary_key=True)
    identification_type = models.ForeignKey(TrtIdentificationTypes, models.DO_NOTHING, db_column='IDENTIFICATION_TYPE')
    identifier = models.CharField(db_column='IDENTIFIER', max_length=20)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_IDENTIFICATION'
        unique_together = (('turtle', 'identification_type', 'identifier'),)


class TrtActivities(models.Model):
    activity_code = models.CharField(db_column='ACTIVITY_CODE', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    nesting = models.CharField(db_column='NESTING', max_length=50)
    new_code = models.CharField(db_column='New_Code', max_length=255, blank=True, null=True)
    display_observation = models.BooleanField(db_column='Display_Observation')

    class Meta:
        managed = False
        db_table = 'TRT_ACTIVITIES'


class TrtObservations(models.Model):
    observation_id = models.AutoField(db_column='OBSERVATION_ID', primary_key=True)
    turtle = models.ForeignKey(TrtTurtles, models.DO_NOTHING, db_column='TURTLE_ID', related_name='observations')
    observation_date = models.DateTimeField(db_column='OBSERVATION_DATE')
    observation_time = models.DateTimeField(db_column='OBSERVATION_TIME', blank=True, null=True)
    observation_date_old = models.DateTimeField(db_column='OBSERVATION_DATE_OLD', blank=True, null=True)
    alive = models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)
    measurer_person = models.ForeignKey(TrtPersons, models.DO_NOTHING, db_column='MEASURER_PERSON_ID', blank=True, null=True, related_name='measurer_person')
    measurer_reporter_person = models.ForeignKey(TrtPersons, models.DO_NOTHING, db_column='MEASURER_REPORTER_PERSON_ID', blank=True, null=True, related_name='measurer_reporter_person')
    tagger_person = models.ForeignKey(TrtPersons, models.DO_NOTHING, db_column='TAGGER_PERSON_ID', blank=True, null=True, related_name='tagger_person')
    reporter_person = models.ForeignKey(TrtPersons, models.DO_NOTHING, db_column='REPORTER_PERSON_ID', blank=True, null=True, related_name='reporter_person')
    place_code = models.ForeignKey(TrtPlaces, models.DO_NOTHING, db_column='PLACE_CODE', blank=True, null=True)
    place_description = models.CharField(db_column='PLACE_DESCRIPTION', max_length=300, blank=True, null=True)
    datum_code = models.ForeignKey(TrtDatumCodes, models.DO_NOTHING, db_column='DATUM_CODE', blank=True, null=True)
    latitude = models.FloatField(db_column='LATITUDE', blank=True, null=True)
    longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)
    latitude_degrees = models.IntegerField(db_column='LATITUDE_DEGREES', blank=True, null=True)
    latitude_minutes = models.FloatField(db_column='LATITUDE_MINUTES', blank=True, null=True)
    latitude_seconds = models.FloatField(db_column='LATITUDE_SECONDS', blank=True, null=True)
    longitude_degrees = models.IntegerField(db_column='LONGITUDE_DEGREES', blank=True, null=True)
    longitude_minutes = models.FloatField(db_column='LONGITUDE_MINUTES', blank=True, null=True)
    longitude_seconds = models.FloatField(db_column='LONGITUDE_SECONDS', blank=True, null=True)
    zone = models.IntegerField(db_column='ZONE', blank=True, null=True)
    easting = models.FloatField(db_column='EASTING', blank=True, null=True)
    northing = models.FloatField(db_column='NORTHING', blank=True, null=True)
    activity_code = models.ForeignKey(TrtActivities, models.DO_NOTHING, db_column='ACTIVITY_CODE', blank=True, null=True)
    beach_position_code = models.ForeignKey(TrtBeachPositions, models.DO_NOTHING, db_column='BEACH_POSITION_CODE', blank=True, null=True)
    condition_code = models.ForeignKey(TrtConditionCodes, models.DO_NOTHING, db_column='CONDITION_CODE', blank=True, null=True)
    nesting = models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)
    clutch_completed = models.CharField(db_column='CLUTCH_COMPLETED', max_length=1, blank=True, null=True)
    number_of_eggs = models.SmallIntegerField(db_column='NUMBER_OF_EGGS', blank=True, null=True)
    egg_count_method = models.ForeignKey(TrtEggCountMethods, models.DO_NOTHING, db_column='EGG_COUNT_METHOD', blank=True, null=True)
    measurements = models.CharField(db_column='MEASUREMENTS', max_length=1)
    action_taken = models.CharField(db_column='ACTION_TAKEN', max_length=255, blank=True, null=True)
    comments = models.TextField(db_column='COMMENTS', blank=True, null=True)
    entered_by = models.CharField(db_column='ENTERED_BY', max_length=50, blank=True, null=True)
    date_entered = models.DateTimeField(db_column='DATE_ENTERED', blank=True, null=True)
    original_observation_id = models.IntegerField(db_column='ORIGINAL_OBSERVATION_ID', blank=True, null=True)
    entry_batch = models.ForeignKey(TrtEntryBatches, models.DO_NOTHING, db_column='ENTRY_BATCH_ID', blank=True, null=True)
    comment_fromrecordedtagstable = models.TextField(db_column='COMMENT_FROMRECORDEDTAGSTABLE', blank=True, null=True)
    scars_left = models.BooleanField(db_column='SCARS_LEFT')
    scars_right = models.BooleanField(db_column='SCARS_RIGHT')
    other_tags = models.CharField(db_column='OTHER_TAGS', max_length=255, blank=True, null=True)
    other_tags_identification_type = models.ForeignKey(TrtIdentificationTypes, models.DO_NOTHING, db_column='OTHER_TAGS_IDENTIFICATION_TYPE', blank=True, null=True)
    transferid = models.IntegerField(db_column='TransferID', blank=True, null=True)
    mund = models.BooleanField(db_column='Mund')
    entered_by_person = models.ForeignKey(TrtPersons, models.DO_NOTHING, db_column='ENTERED_BY_PERSON_ID', blank=True, null=True)
    scars_left_scale_1 = models.BooleanField(db_column='SCARS_LEFT_SCALE_1')
    scars_left_scale_2 = models.BooleanField(db_column='SCARS_LEFT_SCALE_2')
    scars_left_scale_3 = models.BooleanField(db_column='SCARS_LEFT_SCALE_3')
    scars_right_scale_1 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_1')
    scars_right_scale_2 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_2')
    scars_right_scale_3 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_3')
    cc_length_not_measured = models.BooleanField(db_column='CC_LENGTH_Not_Measured')
    cc_notch_length_not_measured = models.BooleanField(db_column='CC_NOTCH_LENGTH_Not_Measured')
    cc_width_not_measured = models.BooleanField(db_column='CC_WIDTH_Not_Measured')
    tagscarnotchecked = models.BooleanField(db_column='TagScarNotChecked')
    didnotcheckforinjury = models.BooleanField(db_column='DidNotCheckForInjury')
    date_convention = models.CharField(db_column='DATE_CONVENTION', max_length=1)
    observation_status = models.CharField(db_column='OBSERVATION_STATUS', max_length=50, blank=True, null=True)
    corrected_date = models.DateTimeField(db_column='CORRECTED_DATE', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_OBSERVATIONS'
        unique_together = (('observation_id', 'turtle'),)

    def __str__(self):
        if self.observation_status:
            return f'{self.observation_id} ({self.get_observation_datetime_awst().isoformat()}) {(self.observation_status)}'
        else:
            return f'{self.observation_id} ({self.get_observation_datetime_awst().isoformat()})'

    def get_observation_datetime_awst(self):
        """Returns a combined observation datetime, in AWST.
        """
        if self.observation_time:
            return datetime(self.observation_date.year, self.observation_date.month, self.observation_date.day, self.observation_time.hour, self.observation_time.minute, tzinfo=settings.AWST)
        else:
            return datetime(self.observation_date.year, self.observation_date.month, self.observation_date.day, 0, 0, tzinfo=settings.AWST)

    def get_observation_datetime_utc(self):
        """Returns a combined observation datetime, in UTC.
        """
        if self.observation_time:
            obs = datetime(self.observation_date.year, self.observation_date.month, self.observation_date.day, self.observation_time.hour, self.observation_time.minute, tzinfo=settings.AWST)
        else:
            obs = datetime(self.observation_date.year, self.observation_date.month, self.observation_date.day, 0, 0, tzinfo=settings.AWST)
        return obs.astimezone(settings.UTC)

    def get_point(self):
        """Returns a geometry point as WGS84.
        """
        if not self.longitude or not self.latitude:
            return None
        if self.datum_code:
            if self.datum_code.datum_code == "AGD66":
                datum = 4202
            elif self.datum_code.datum_code == "AGD66":
                datum = 4203
            elif self.datum_code.datum_code == "GDA94":
                datum = 4283
            elif self.datum_code.datum_code == "WGS84":
                datum = 4326
        else:
            datum = 4326
        geom = Point(x=self.longitude, y=self.latitude, srid=datum)
        geom.transform(4326)
        return geom


class TrtDamage(models.Model):
    observation = models.OneToOneField(TrtObservations, models.DO_NOTHING, db_column='OBSERVATION_ID', primary_key=True)
    body_part = models.ForeignKey(TrtBodyParts, models.DO_NOTHING, db_column='BODY_PART')
    damage_code = models.ForeignKey(TrtDamageCodes, models.DO_NOTHING, db_column='DAMAGE_CODE')
    damage_cause_code = models.ForeignKey(TrtDamageCauseCodes, models.DO_NOTHING, db_column='DAMAGE_CAUSE_CODE', blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_DAMAGE'
        unique_together = (('observation', 'body_part', 'body_part'),)


class TrtMeasurements(models.Model):
    observation = models.OneToOneField(TrtObservations, models.DO_NOTHING, db_column='OBSERVATION_ID', primary_key=True)
    measurement_type = models.ForeignKey(TrtMeasurementTypes, models.DO_NOTHING, db_column='MEASUREMENT_TYPE')
    measurement_value = models.FloatField(db_column='MEASUREMENT_VALUE')
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_MEASUREMENTS'
        unique_together = (('observation', 'measurement_type'),)


class TrtPitTags(models.Model):
    pit_tag_id = models.CharField(db_column='PIT_TAG_ID', primary_key=True, max_length=50)
    issue_location = models.CharField(db_column='ISSUE_LOCATION', max_length=50, blank=True, null=True)
    custodian_person_id = models.IntegerField(db_column='CUSTODIAN_PERSON_ID', blank=True, null=True)
    turtle = models.ForeignKey(TrtTurtles, models.DO_NOTHING, db_column='TURTLE_ID', related_name='pit_tags', blank=True, null=True)
    pit_tag_status = models.CharField(db_column='PIT_TAG_STATUS', max_length=10, blank=True, null=True)
    return_date = models.DateTimeField(db_column='RETURN_DATE', blank=True, null=True)
    return_condition = models.CharField(db_column='RETURN_CONDITION', max_length=50, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    field_person_id = models.IntegerField(db_column='FIELD_PERSON_ID', blank=True, null=True)
    tag_order_id = models.IntegerField(db_column='TAG_ORDER_ID', blank=True, null=True)
    batch_number = models.CharField(db_column='BATCH_NUMBER', max_length=50, blank=True, null=True)
    box_number = models.CharField(db_column='BOX_NUMBER', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_PIT_TAGS'
        unique_together = (('pit_tag_id', 'turtle'),)

    def __str__(self):
        return self.pit_tag_id


class TrtPitTagStatus(models.Model):
    pit_tag_status = models.CharField(db_column='PIT_TAG_STATUS', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_PIT_TAG_STATUS'


class TrtPitTagStates(models.Model):
    pit_tag_state = models.CharField(db_column='PIT_TAG_STATE', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    pit_tag_status = models.ForeignKey(TrtPitTagStatus, models.DO_NOTHING, db_column='PIT_TAG_STATUS')
    existing_tag_list = models.BooleanField(db_column='EXISTING_TAG_LIST')
    new_tag_list = models.BooleanField(db_column='NEW_TAG_LIST')

    class Meta:
        managed = False
        db_table = 'TRT_PIT_TAG_STATES'


class TrtRecordedIdentification(models.Model):
    recorded_identification_id = models.AutoField(db_column='RECORDED_IDENTIFICATION_ID', primary_key=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID')
    turtle = models.ForeignKey(TrtIdentification, models.DO_NOTHING, db_column='TURTLE_ID')
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_RECORDED_IDENTIFICATION'


class TrtRecordedPitTags(models.Model):
    recorded_pit_tag_id = models.AutoField(db_column='RECORDED_PIT_TAG_ID', primary_key=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID')
    pit_tag_id = models.CharField(db_column='PIT_TAG_ID', max_length=50)
    pit_tag_state = models.ForeignKey(TrtPitTagStates, models.DO_NOTHING, db_column='PIT_TAG_STATE')
    pit_tag_position = models.CharField(db_column='PIT_TAG_POSITION', max_length=10, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    turtle_id = models.IntegerField(db_column='TURTLE_ID')
    checked = models.BooleanField(db_column='Checked')

    class Meta:
        managed = False
        db_table = 'TRT_RECORDED_PIT_TAGS'


class TrtRecordedTags(models.Model):
    recorded_tag_id = models.AutoField(db_column='RECORDED_TAG_ID', primary_key=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID')
    tag_id = models.CharField(db_column='TAG_ID', max_length=10)
    other_tag_id = models.CharField(db_column='OTHER_TAG_ID', max_length=10, blank=True, null=True)
    side = models.CharField(db_column='SIDE', max_length=1, blank=True, null=True)
    tag_state = models.CharField(db_column='TAG_STATE', max_length=10, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    tag_position = models.SmallIntegerField(db_column='TAG_POSITION', blank=True, null=True)
    barnacles = models.BooleanField(db_column='BARNACLES')
    turtle_id = models.IntegerField(db_column='TURTLE_ID')

    class Meta:
        managed = False
        db_table = 'TRT_RECORDED_TAGS'


class TrtTissueTypes(models.Model):
    tissue_type = models.CharField(db_column='TISSUE_TYPE', primary_key=True, max_length=5)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_TISSUE_TYPES'


class TrtSamples(models.Model):
    sample_id = models.AutoField(db_column='SAMPLE_ID', primary_key=True)
    turtle = models.ForeignKey(TrtTurtles, models.DO_NOTHING, db_column='TURTLE_ID')
    sample_date = models.DateTimeField(db_column='SAMPLE_DATE', blank=True, null=True)
    tissue_type = models.ForeignKey(TrtTissueTypes, models.DO_NOTHING, db_column='TISSUE_TYPE')
    arsenic = models.FloatField(db_column='ARSENIC', blank=True, null=True)
    selenium = models.FloatField(db_column='SELENIUM', blank=True, null=True)
    zinc = models.FloatField(db_column='ZINC', blank=True, null=True)
    cadmium = models.FloatField(db_column='CADMIUM', blank=True, null=True)
    copper = models.FloatField(db_column='COPPER', blank=True, null=True)
    lead = models.FloatField(db_column='LEAD', blank=True, null=True)
    mercury = models.FloatField(db_column='MERCURY', blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    observation_id = models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)
    sample_label = models.CharField(db_column='SAMPLE_LABEL', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_SAMPLES'


class TrtSighting(models.Model):
    sightingid = models.AutoField(db_column='SIGHTINGID', primary_key=True)
    observation_time = models.DateTimeField(db_column='OBSERVATION_TIME', blank=True, null=True)
    observation_date = models.DateTimeField(db_column='OBSERVATION_DATE', blank=True, null=True)
    alive = models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)
    species_code = models.CharField(db_column='SPECIES_CODE', max_length=2, blank=True, null=True)
    sex = models.CharField(db_column='SEX', max_length=1, blank=True, null=True)
    location_code = models.CharField(db_column='LOCATION_CODE', max_length=2, blank=True, null=True)
    turtle_status = models.CharField(db_column='TURTLE_STATUS', max_length=1, blank=True, null=True)
    place_code = models.CharField(db_column='PLACE_CODE', max_length=4, blank=True, null=True)
    activity_code = models.CharField(db_column='ACTIVITY_CODE', max_length=2, blank=True, null=True)
    beach_position_code = models.CharField(db_column='BEACH_POSITION_CODE', max_length=2, blank=True, null=True)
    datum_code = models.CharField(db_column='DATUM_CODE', max_length=5, blank=True, null=True)
    latitude = models.CharField(db_column='LATITUDE', max_length=7, blank=True, null=True)
    longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    entered_by_person_id = models.IntegerField(db_column='ENTERED_BY_PERSON_ID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_SIGHTING'


class TrtTagStatus(models.Model):
    tag_status = models.CharField(db_column='TAG_STATUS', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)

    class Meta:
        managed = False
        db_table = 'TRT_TAG_STATUS'


class TrtTags(models.Model):
    tag_id = models.CharField(db_column='TAG_ID', primary_key=True, max_length=10)
    tag_order_id = models.IntegerField(db_column='TAG_ORDER_ID', blank=True, null=True)
    issue_location = models.CharField(db_column='ISSUE_LOCATION', max_length=50, blank=True, null=True)
    custodian_person_id = models.IntegerField(db_column='CUSTODIAN_PERSON_ID', blank=True, null=True)
    turtle = models.ForeignKey(TrtTurtles, models.DO_NOTHING, db_column='TURTLE_ID', related_name='tags', blank=True, null=True)
    side = models.CharField(db_column='SIDE', max_length=1, blank=True, null=True)
    tag_status = models.ForeignKey(TrtTagStatus, models.DO_NOTHING, db_column='TAG_STATUS', blank=True, null=True)
    return_date = models.DateTimeField(db_column='RETURN_DATE', blank=True, null=True)
    return_condition = models.CharField(db_column='RETURN_CONDITION', max_length=50, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)
    field_person_id = models.IntegerField(db_column='FIELD_PERSON_ID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_TAGS'
        unique_together = (('tag_id', 'turtle'),)

    def __str__(self):
        return self.tag_id


class TrtTagOrders(models.Model):
    tag_order_id = models.AutoField(db_column='TAG_ORDER_ID', primary_key=True)
    order_date = models.DateTimeField(db_column='ORDER_DATE', blank=True, null=True)
    order_number = models.CharField(db_column='ORDER_NUMBER', max_length=20)
    tag_prefix = models.CharField(db_column='TAG_PREFIX', max_length=10, blank=True, null=True)
    start_tag_number = models.IntegerField(db_column='START_TAG_NUMBER', blank=True, null=True)
    end_tag_number = models.IntegerField(db_column='END_TAG_NUMBER', blank=True, null=True)
    total_tags = models.SmallIntegerField(db_column='TOTAL_TAGS', blank=True, null=True)
    date_received = models.DateTimeField(db_column='DATE_RECEIVED', blank=True, null=True)
    paid_by = models.CharField(db_column='PAID_BY', max_length=255, blank=True, null=True)
    comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TRT_TAG_ORDERS'


class TrtTagStates(models.Model):
    tag_state = models.CharField(db_column='TAG_STATE', primary_key=True, max_length=10)
    description = models.CharField(db_column='DESCRIPTION', max_length=50)
    tag_status = models.CharField(db_column='TAG_STATUS', max_length=10, blank=True, null=True)
    existing_tag_list = models.BooleanField(db_column='EXISTING_TAG_LIST')
    new_tag_list = models.BooleanField(db_column='NEW_TAG_LIST')

    class Meta:
        managed = False
        db_table = 'TRT_TAG_STATES'


class TrtYesNo(models.Model):
    code = models.CharField(db_column='CODE', primary_key=True, max_length=1)
    description = models.CharField(db_column='DESCRIPTION', max_length=10)

    class Meta:
        managed = False
        db_table = 'TRT_YES_NO'
