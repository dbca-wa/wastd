from django.contrib.gis.db import models
import uuid

class TrtActivities(models.Model):
    activity_code = models.CharField(
        db_column="ACTIVITY_CODE", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    nesting = models.CharField(
        db_column="NESTING", max_length=50
    )  # Field name made lowercase.
    new_code = models.CharField(
        db_column="New_Code", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    display_observation = models.BooleanField(
        db_column="Display_Observation"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_ACTIVITIES"

    def __str__(self):
        return f"{self.description}"


class TrtBeachPositions(models.Model):
    beach_position_code = models.CharField(
        db_column="BEACH_POSITION_CODE", primary_key=True, max_length=2
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    new_code = models.CharField(
        db_column="New_Code", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_BEACH_POSITIONS"


class TrtBodyParts(models.Model):
    body_part = models.CharField(
        db_column="BODY_PART", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    flipper = models.BooleanField(db_column="FLIPPER")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_BODY_PARTS"

    def __str__(self):
        return f"{self.description}"


class TrtCauseOfDeath(models.Model):
    cause_of_death = models.CharField(
        db_column="CAUSE_OF_DEATH", primary_key=True, max_length=2
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_CAUSE_OF_DEATH"


class TrtConditionCodes(models.Model):
    condition_code = models.CharField(
        db_column="CONDITION_CODE", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_CONDITION_CODES"

    def __str__(self):
        return f"{self.description}"


class TrtDamage(models.Model):
    observation = models.OneToOneField(
        "TrtObservations", models.CASCADE, db_column="OBSERVATION_ID", primary_key=True
    )  # Field name made lowercase.
    body_part = models.ForeignKey(
        TrtBodyParts, models.CASCADE, db_column="BODY_PART"
    )  # Field name made lowercase.
    damage_code = models.ForeignKey(
        "TrtDamageCodes", models.CASCADE, db_column="DAMAGE_CODE"
    )  # Field name made lowercase.
    damage_cause_code = models.ForeignKey(
        "TrtDamageCauseCodes",
        models.SET_NULL,
        db_column="DAMAGE_CAUSE_CODE",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DAMAGE"
        constraints = [
            models.UniqueConstraint(
                fields=["observation", "body_part"],
                name="unique_observation_body_part"
            )
        ]


class TrtDamageCause(models.Model):
    observation_id = models.IntegerField(
        db_column="OBSERVATION_ID"
    )  # Field name made lowercase.
    body_part = models.CharField(
        db_column="BODY_PART", max_length=1
    )  # Field name made lowercase.
    damage_code = models.CharField(
        db_column="DAMAGE_CODE", max_length=1
    )  # Field name made lowercase.
    damage_cause_code = models.CharField(
        db_column="DAMAGE_CAUSE_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DAMAGE_CAUSE"


class TrtDamageCauseCodes(models.Model):
    damage_cause_code = models.CharField(
        db_column="DAMAGE_CAUSE_CODE", primary_key=True, max_length=2
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DAMAGE_CAUSE_CODES"

    def __str__(self):
        return f"{self.description}"


class TrtDamageCodes(models.Model):
    damage_code = models.CharField(
        db_column="DAMAGE_CODE", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    flipper = models.BooleanField(db_column="FLIPPER")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DAMAGE_CODES"

    def __str__(self):
        return f"{self.description}"


class TrtDataChanged(models.Model):
    """
    Used to store data entries while they are being edited and validated.
    When processed using the sql stored procedure, the data is copied to the database
    """

    trt_data_changed_id = models.AutoField(
        db_column="TRT_DATA_CHANGED_ID", primary_key=True
    )  # Field name made lowercase.
    datachanged_date = models.DateTimeField(
        db_column="DATACHANGED_DATE", blank=True, null=True
    )  # Field name made lowercase.
    datachangedby = models.CharField(
        db_column="DATACHANGEDBY", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    comment = models.CharField(
        db_column="COMMENT", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DATA_CHANGED"


class TrtDataEntry(models.Model):
    SEX_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("I", "Indeterminate"),
    ]
    TAG_POSITION_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
    ]
    data_entry_id = models.AutoField(
        db_column="DATA_ENTRY_ID", primary_key=True
    )  # Field name made lowercase.
    entry_batch = models.ForeignKey(
        "TrtEntryBatches", models.CASCADE, db_column="ENTRY_BATCH_ID"
    )  # Field name made lowercase.
    user_entry_id = models.IntegerField(
        db_column="USER_ENTRY_ID", blank=True, null=True
    )  # Field name made lowercase.
    turtle_id = models.ForeignKey(
        "TrtTurtles", models.SET_NULL, db_column="TURTLE_ID", blank=True, null=True
    )  # fake foreign key #models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
    observation_id = models.ForeignKey(
        "TrtObservations",
        models.SET_NULL,
        db_column="OBSERVATION_ID",
        blank=True,
        null=True,
    )  # fake foreign key #models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.
    do_not_process = models.BooleanField(
        db_column="DO_NOT_PROCESS"
    )  # Field name made lowercase.
    recapture_left_tag_id = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_LEFT_TAG_ID",
        blank=True,
        null=True,
        related_name="recapturelefttag",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_LEFT_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recapture_left_tag_id_2 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_LEFT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="recapturelefttag2",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_LEFT_TAG_ID_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recapture_right_tag_id = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_RIGHT_TAG_ID",
        blank=True,
        null=True,
        related_name="recapturerighttag",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recapture_right_tag_id_2 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_RIGHT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="recapturerighttag2",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recapture_pittag_id = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="RECAPTURE_PIT_TAG_ID",
        blank=True,
        null=True,
        related_name="recapturepittag",
    )  # fake foreign key for left pit tag #models.CharField(db_column='recapture_pittag_id', max_length=50, blank=True, null=True)  # Field name made lowercase.
    other_left_tag = models.CharField(
        db_column="OTHER_LEFT_TAG", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    other_right_tag = models.CharField(
        db_column="OTHER_RIGHT_TAG", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    new_left_tag_id = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="NEW_LEFT_TAG_ID",
        blank=True,
        null=True,
        related_name="lefttag",
    )  # fake foreign key #models.CharField(db_column='NEW_LEFT_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    new_left_tag_id_2 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="NEW_LEFT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="lefttag2",
    )  # fake foreign key #models.CharField(db_column='NEW_LEFT_TAG_ID_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    new_right_tag_id = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="NEW_RIGHT_TAG_ID",
        blank=True,
        null=True,
        related_name="righttag",
    )  # fake foreign key #models.CharField(db_column='NEW_RIGHT_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    new_right_tag_id_2 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="NEW_RIGHT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="righttag2",
    )  # fake foreign key #models.CharField(db_column='NEW_RIGHT_TAG_ID_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    new_pittag_id = models.ForeignKey(
        "TrtPitTags", models.SET_NULL, db_column="NEW_PIT_TAG_ID", blank=True, null=True
    )  # fake foreign key for left pit tag #models.CharField(db_column='NEW_pittag_id', max_length=50, blank=True, null=True)  # Field name made lowercase.
    alive = models.ForeignKey(
        "TrtYesNo",
        models.SET_NULL,
        db_column="ALIVE",
        blank=True,
        null=True,
        related_name="nesting",
    )  # fake foreign key #models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    place_code = models.ForeignKey(
        "TrtPlaces", models.SET_NULL, db_column="PLACE_CODE", blank=True, null=True
    )  # fake foreign key $models.CharField(db_column='PLACE_CODE', max_length=4, blank=True, null=True)  # Field name made lowercase.
    observation_date = models.DateTimeField(
        db_column="OBSERVATION_DATE", blank=True, null=True
    )  # Field name made lowercase.
    observation_time = models.DateTimeField(
        db_column="OBSERVATION_TIME", blank=True, null=True
    )  # Field name made lowercase.
    nesting = models.ForeignKey(
        "TrtYesNo", models.SET_NULL, db_column="NESTING", blank=True, null=True, limit_choices_to={'code__in': ['D', 'N', 'Y', 'P']}
    )  # fake foreign key #models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)  # Field name made lowercase.
    species_code = models.ForeignKey(
        "TrtSpecies", models.SET_NULL, db_column="SPECIES_CODE", blank=True, null=True
    )  # fake foreign key #models.CharField(db_column='SPECIES_CODE', max_length=2, blank=True, null=True)  # Field name made lowercase.
    identification_confidence = models.CharField(
        db_column="IDENTIFICATION_CONFIDENCE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    sex = models.CharField(
        db_column="SEX", max_length=1, blank=True, null=True, choices=SEX_CHOICES
    )  # Field name made lowercase.
    curved_carapace_length = models.IntegerField(
        db_column="CURVED_CARAPACE_LENGTH", blank=True, null=True
    )  # Field name made lowercase.
    curved_carapace_width = models.IntegerField(
        db_column="CURVED_CARAPACE_WIDTH", blank=True, null=True
    )  # Field name made lowercase.
    activity_code = models.ForeignKey(
        "TrtActivities",
        models.SET_NULL,
        db_column="ACTIVITY_CODE",
        blank=True,
        null=True,
    )  # fake foreign key #models.CharField(db_column='ACTIVITY_CODE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    beach_position_code = models.CharField(
        db_column="BEACH_POSITION_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    damage_carapace = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_CARAPACE",
        blank=True,
        null=True,
        related_name="carapace",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_CARAPACE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_lff = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_LFF",
        blank=True,
        null=True,
        related_name="lff",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_LFF', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_rff = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_RFF",
        blank=True,
        null=True,
        related_name="rff",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_RFF', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_lhf = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_LHF",
        blank=True,
        null=True,
        related_name="lhf",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_LHF', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_rhf = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_RHF",
        blank=True,
        null=True,
        related_name="rhf",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_RHF', max_length=1, blank=True, null=True)  # Field name made lowercase.
    body_part_1 = models.ForeignKey(
        "TrtBodyParts",
        models.SET_NULL,
        db_column="BODY_PART_1",
        blank=True,
        null=True,
        related_name="bp1",
    )  # fake foreign key #models.CharField(db_column='BODY_PART_1', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_code_1 = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_CODE_1",
        blank=True,
        null=True,
        related_name="dc1",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_CODE_1', max_length=1, blank=True, null=True)  # Field name made lowercase.
    body_part_2 = models.ForeignKey(
        "TrtBodyParts",
        models.SET_NULL,
        db_column="BODY_PART_2",
        blank=True,
        null=True,
        related_name="bp2",
    )  # fake foreign key #models.CharField(db_column='BODY_PART_2', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_code_2 = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_CODE_2",
        blank=True,
        null=True,
        related_name="dc2",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_CODE_2', max_length=1, blank=True, null=True)  # Field name made lowercase.
    egg_count = models.IntegerField(
        db_column="EGG_COUNT", blank=True, null=True
    )  # Field name made lowercase.
    egg_count_method = models.ForeignKey(
        "TrtEggCountMethods",
        models.SET_NULL,
        db_column="EGG_COUNT_METHOD", 
        max_length=3, 
        blank=True, 
        null=True,
        related_name="eggcountmethod",
    )  # Field name made lowercase.
    clutch_completed = models.ForeignKey(
        "TrtYesNo",
        models.SET_NULL,
        db_column="CLUTCH_COMPLETED",
        blank=True,
        null=True,
        related_name="clutchcompleted"
    )
    # clutch_completed = models.CharField(
    #     db_column="CLUTCH_COMPLETED", max_length=1, blank=True, null=True
    # )  # Field name made lowercase.
    measured_by = models.CharField(
        db_column="MEASURED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase. Used by old MSAccess frontend
    measured_by_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="MEASURED_BY_ID",
        blank=True,
        null=True,
        related_name="measuredby",
    )
    recorded_by = models.CharField(
        db_column="RECORDED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.Used by old MSAccess frontend
    recorded_by_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="RECORDED_BY_ID",
        blank=True,
        null=True,
        related_name="recordedby",
    )
    tagged_by = models.CharField(
        db_column="TAGGED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.Used by old MSAccess frontend
    tagged_by_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="TAGGED_BY_ID",
        blank=True,
        null=True,
        related_name="taggedby",
    )
    entered_by = models.CharField(
        db_column="ENTERED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.Used by old MSAccess frontend
    entered_by_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="ENTERED_BY_ID",
        blank=True,
        null=True,
        related_name="enteredby",
    )
    measured_recorded_by = models.CharField(
        db_column="MEASURED_RECORDED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    measured_recorded_by_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="MEASURED_RECORDED_BY_ID",
        blank=True,
        null=True,
        related_name="measuredrecordedby",
    )
    measurement_type_1 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_1",
        blank=True,
        null=True,
        related_name="measuretype1",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_1', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_1 = models.FloatField(
        db_column="MEASUREMENT_VALUE_1", blank=True, null=True
    )  # Field name made lowercase.
    measurement_type_2 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_2",
        blank=True,
        null=True,
        related_name="measuretype2",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_2 = models.FloatField(
        db_column="MEASUREMENT_VALUE_2", blank=True, null=True
    )  # Field name made lowercase.
    datum_code = models.CharField(
        db_column="DATUM_CODE", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    zone = models.IntegerField(
        db_column="ZONE", blank=True, null=True
    )  # Field name made lowercase.
    easting = models.FloatField(
        db_column="EASTING", blank=True, null=True
    )  # Field name made lowercase.
    northing = models.FloatField(
        db_column="NORTHING", blank=True, null=True
    )  # Field name made lowercase.
    latitude = models.FloatField(
        db_column="LATITUDE", blank=True, null=True
    )  # Field name made lowercase.
    longitude = models.FloatField(
        db_column="LONGITUDE", blank=True, null=True
    )  # Field name made lowercase.
    latitude_degrees = models.IntegerField(
        db_column="LATITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_minutes = models.FloatField(
        db_column="LATITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_seconds = models.FloatField(
        db_column="LATITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    longitude_degrees = models.IntegerField(
        db_column="LONGITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_minutes = models.FloatField(
        db_column="LONGITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_seconds = models.FloatField(
        db_column="LONGITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    identification_type = models.ForeignKey(
        "TrtIdentificationTypes",
        models.CASCADE,
        db_column="IDENTIFICATION_TYPE",
        blank=True,
        null=True
    )
    identifier = models.CharField(
        db_column="IDENTIFIER", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    comment_fromrecordedtagstable = models.CharField(
        db_column="COMMENT_FROMRECORDEDTAGSTABLE", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    scars_left = models.BooleanField(
        db_column="SCARS_LEFT"
    )  # Field name made lowercase.
    scars_right = models.BooleanField(
        db_column="SCARS_RIGHT"
    )  # Field name made lowercase.
    other_tags = models.CharField(
        db_column="OTHER_TAGS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    other_tags_identification_type = models.CharField(
        db_column="OTHER_TAGS_IDENTIFICATION_TYPE", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    scars_left_scale_1 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_1"
    )  # Field name made lowercase.
    scars_left_scale_2 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_2"
    )  # Field name made lowercase.
    scars_left_scale_3 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_3"
    )  # Field name made lowercase.
    scars_right_scale_1 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_1"
    )  # Field name made lowercase.
    scars_right_scale_2 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_2"
    )  # Field name made lowercase.
    scars_right_scale_3 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_3"
    )  # Field name made lowercase.
    cc_length_not_measured = models.BooleanField(
        db_column="CC_LENGTH_NOT_MEASURED"
    )  # Field name made lowercase.
    cc_notch_length_not_measured = models.BooleanField(
        db_column="CC_NOTCH_LENGTH_NOT_MEASURED"
    )  # Field name made lowercase.
    cc_width_not_measured = models.BooleanField(
        db_column="CC_WIDTH_NOT_MEASURED"
    )  # Field name made lowercase.
    tagscarnotchecked = models.BooleanField(
        db_column="TAGSCARNOTCHECKED"
    )  # Field name made lowercase.
    didnotcheckforinjury = models.BooleanField(
        db_column="DIDNOTCHECKFORINJURY"
    )  # Field name made lowercase.
    comments = models.TextField(
        db_column="COMMENTS", blank=True, null=True
    )  # Field name made lowercase.
    error_number = models.IntegerField(
        db_column="ERROR_NUMBER", blank=True, null=True
    )  # Field name made lowercase.
    error_message = models.CharField(
        db_column="ERROR_MESSAGE", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    recapture_left_tag_id_3 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_LEFT_TAG_ID_3",
        blank=True,
        null=True,
        related_name="recapturelefttag3",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_LEFT_TAG_ID_3', max_length=10, blank=True, null=True)  # Field name made lowercase.
    recapture_right_tag_id_3 = models.ForeignKey(
        "TrtTags",
        models.SET_NULL,
        db_column="RECAPTURE_RIGHT_TAG_ID_3",
        blank=True,
        null=True,
        related_name="recapturerighttag3",
    )  # fake foreign key #models.CharField(db_column='RECAPTURE_RIGHT_TAG_ID_3', max_length=10, blank=True, null=True)  # Field name made lowercase.
    body_part_3 = models.ForeignKey(
        "TrtBodyParts",
        models.SET_NULL,
        db_column="BODY_PART_3",
        blank=True,
        null=True,
        related_name="bp3",
    )   # fake foreign key #models.CharField(db_column='BODY_PART_3', max_length=1, blank=True, null=True)  # Field name made lowercase.
    damage_code_3 = models.ForeignKey(
        "TrtDamageCodes",
        models.SET_NULL,
        db_column="DAMAGE_CODE_3",
        blank=True,
        null=True,
        related_name="dc3",
    )  # fake foreign key #models.CharField(db_column='DAMAGE_CODE_3', max_length=1, blank=True, null=True)  # Field name made lowercase.
    tissue_type_1 = models.ForeignKey(
        "TrtTissueTypes",
        models.SET_NULL,
        db_column="TISSUE_TYPE_1",
        blank=True,
        null=True,
        related_name="tt1",
    )  # fake foreign key #models.CharField(db_column='TISSUE_TYPE_1', max_length=5, blank=True, null=True)  # Field name made lowercase.
    sample_label_1 = models.CharField(
        db_column="SAMPLE_LABEL_1", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    tissue_type_2 = models.ForeignKey(
        "TrtTissueTypes",
        models.SET_NULL,
        db_column="TISSUE_TYPE_2",
        blank=True,
        null=True,
        related_name="tt2",
    )  # fake foreign key #models.CharField(db_column='TISSUE_TYPE_2', max_length=5, blank=True, null=True)  # Field name made lowercase.
    sample_label_2 = models.CharField(
        db_column="SAMPLE_LABEL_2", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    turtle_comments = models.CharField(
        db_column="TURTLE_COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    recapture_pittag_id_2 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="RECAPTURE_PIT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="recapturepittag2",
    )  # fake foreign key for right pit tag #models.CharField(db_column='recapture_pittag_id_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    new_pittag_id_2 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="NEW_PIT_TAG_ID_2",
        blank=True,
        null=True,
        related_name="newpittag2",
    )  # fake foreign key for right pit tag #models.CharField(db_column='NEW_PIT_TAG_ID_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    # Flipper tag states
    recapture_left_tag_state = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='RECAPTURE_LEFT_TAG_STATE')
    recapture_left_tag_state_2 = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='RECAPTURE_LEFT_TAG_STATE_2')
    recapture_right_tag_state = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='RECAPTURE_RIGHT_TAG_STATE')
    recapture_right_tag_state_2 = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='RECAPTURE_RIGHT_TAG_STATE_2')
    new_left_tag_state = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='NEW_LEFT_TAG_STATE')
    new_left_tag_state_2 = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='NEW_LEFT_TAG_STATE_2')
    new_right_tag_state = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='NEW_RIGHT_TAG_STATE')
    new_right_tag_state_2 = models.ForeignKey('TrtTagStates', models.SET_NULL, null=True, related_name='+', db_column='NEW_RIGHT_TAG_STATE_2')

    # Flipper tag position
    recapture_left_tag_position = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='RECAPTURE_LEFT_TAG_POSITION')
    recapture_left_tag_position_2 = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='RECAPTURE_LEFT_TAG_POSITION_2')
    recapture_right_tag_position = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='RECAPTURE_RIGHT_TAG_POSITION')
    recapture_right_tag_position_2 = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='RECAPTURE_RIGHT_TAG_POSITION_2')
    new_left_tag_position = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='NEW_LEFT_TAG_POSITION')
    new_left_tag_position_2 = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='NEW_LEFT_TAG_POSITION_2')
    new_right_tag_position = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='NEW_RIGHT_TAG_POSITION')
    new_right_tag_position_2 = models.SmallIntegerField(choices=TAG_POSITION_CHOICES, null=True, db_column='NEW_RIGHT_TAG_POSITION_2')

    # Flipper tag barnacles
    recapture_left_tag_barnacles = models.BooleanField(default=False, db_column='RECAPTURE_LEFT_TAG_BARNACLES')
    recapture_left_tag_barnacles_2 = models.BooleanField(default=False, db_column='RECAPTURE_LEFT_TAG_BARNACLES_2')
    recapture_right_tag_barnacles = models.BooleanField(default=False, db_column='RECAPTURE_RIGHT_TAG_BARNACLES')
    recapture_right_tag_barnacles_2 = models.BooleanField(default=False, db_column='RECAPTURE_RIGHT_TAG_BARNACLES_2')
    new_left_tag_barnacles = models.BooleanField(default=False, db_column='NEW_LEFT_TAG_BARNACLES')
    new_left_tag_barnacles_2 = models.BooleanField(default=False, db_column='NEW_LEFT_TAG_BARNACLES_2')
    new_right_tag_barnacles = models.BooleanField(default=False, db_column='NEW_RIGHT_TAG_BARNACLES')
    new_right_tag_barnacles_2 = models.BooleanField(default=False, db_column='NEW_RIGHT_TAG_BARNACLES_2')
    
    # Measurements
    # Curved carapace length min
    curved_carapace_length_notch = models.IntegerField(
        db_column="CURVED_CARAPACE_LENGTH_NOTCH", blank=True, null=True
    )  
    # More measurements
    measurement_type_3 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_3",
        blank=True,
        null=True,
        related_name="measuretype3",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_3 = models.FloatField(
        db_column="MEASUREMENT_VALUE_3", blank=True, null=True
    )  # Field name made lowercase.
    
    measurement_type_4 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_4",
        blank=True,
        null=True,
        related_name="measuretype4",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_4 = models.FloatField(
        db_column="MEASUREMENT_VALUE_4", blank=True, null=True
    )  # Field name made lowercase.
    
    measurement_type_5 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_5",
        blank=True,
        null=True,
        related_name="measuretype5",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_5 = models.FloatField(
        db_column="MEASUREMENT_VALUE_5", blank=True, null=True
    )  # Field name made lowercase.
    
    measurement_type_6 = models.ForeignKey(
        "TrtMeasurementTypes",
        models.SET_NULL,
        db_column="MEASUREMENT_TYPE_6",
        blank=True,
        null=True,
        related_name="measuretype6",
    )  # fake foreign key #models.CharField(db_column='MEASUREMENT_TYPE_2', max_length=10, blank=True, null=True)  # Field name made lowercase.
    measurement_value_6 = models.FloatField(
        db_column="MEASUREMENT_VALUE_6", blank=True, null=True
    )  # Field name made lowercase.
    
    
    flipper_tag_check = models.ForeignKey(
        "TrtYesNo",
        on_delete=models.CASCADE,
        related_name='flipper_tag_entries',
        db_column='FLIPPER_TAG_CHECK',
        limit_choices_to={'code__in': ['D', 'N', 'Y']}
    )
    pit_tag_check = models.ForeignKey(
        "TrtYesNo",
        on_delete=models.CASCADE,
        related_name='pit_tag_entries',
        db_column='PIT_TAG_CHECK',
        limit_choices_to={'code__in': ['D', 'N', 'Y']}
    )
    injury_check = models.ForeignKey(
        "TrtYesNo",
        on_delete=models.CASCADE,
        related_name='injury_entries',
        db_column='INJURY_CHECK',
        limit_choices_to={'code__in': ['D', 'N', 'Y']} 
    )
    scar_check = models.ForeignKey(
        "TrtYesNo",
        on_delete=models.CASCADE,
        related_name='scar_entries',
        db_column='SCAR_CHECK',
        limit_choices_to={'code__in': ['D', 'N', 'Y']}
    )
    
    recapture_pittag_id_3 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="RECAPTURE_PIT_TAG_ID_3",
        blank=True,
        null=True,
        related_name="recapturepittag3",
    )  # fake foreign key for right pit tag #models.CharField(db_column='recapture_pittag_id_3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    new_pittag_id_3 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="NEW_PIT_TAG_ID_3",
        blank=True,
        null=True,
        related_name="newpittag3",
    )  # fake foreign key for right pit tag #models.CharField(db_column='NEW_PIT_TAG_ID_3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    recapture_pittag_id_4 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="RECAPTURE_PIT_TAG_ID_4",
        blank=True,
        null=True,
        related_name="recapturepittag4",
    )  # fake foreign key for right pit tag #models.CharField(db_column='recapture_pittag_id_4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    new_pittag_id_4 = models.ForeignKey(
        "TrtPitTags",
        models.SET_NULL,
        db_column="NEW_PIT_TAG_ID_4",
        blank=True,
        null=True,
        related_name="newpittag4",
    )  # fake foreign key for right pit tag #models.CharField(db_column='NEW_PIT_TAG_ID_4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    new_pit_tag_sticker_present = models.BooleanField(default=False, db_column='NEW_PIT_TAG_STICKER_PRESENT')
    new_pit_tag_2_sticker_present = models.BooleanField(default=False, db_column='NEW_PIT_TAG_2_STICKER_PRESENT')
    new_pit_tag_3_sticker_present = models.BooleanField(default=False, db_column='NEW_PIT_TAG_3_STICKER_PRESENT')
    new_pit_tag_4_sticker_present = models.BooleanField(default=False, db_column='NEW_PIT_TAG_4_STICKER_PRESENT')


    dud_filpper_tag = models.CharField(
        max_length=10,
        db_column="DUD_FLIPPER_TAG",
        blank=True,
        null=True,
    )  
    dud_filpper_tag_2 = models.CharField(
        max_length=10,
        db_column="DUD_FLIPPER_TAG_2",
        blank=True,
        null=True,
    )
    dud_pit_tag = models.CharField(
        max_length=50,
        db_column="DUD_PIT_TAG",
        blank=True,
        null=True,
    )
    dud_pit_tag_2 = models.CharField(
        max_length=50,
        db_column="DUD_PIT_TAG_2",
        blank=True,
        null=True,
    )
    class Meta:
        managed = False
        db_table = "TRT_DATA_ENTRY"
        constraints = [
            models.UniqueConstraint(
                fields=["entry_batch", "user_entry_id"],
                name="unique_entry_batch_user_entry_id"
            )
        ]
        
        ordering = ["-data_entry_id"]

    def __str__(self):
        return f"{self.data_entry_id}"


class TrtDataEntryExceptions(models.Model):
    entry_batch_id = models.IntegerField(
        db_column="ENTRY_BATCH_ID", primary_key=True
    )  # Field name made lowercase.
    data_entry_id = models.IntegerField(
        db_column="DATA_ENTRY_ID"
    )  # Field name made lowercase.
    turtle_id = models.IntegerField(
        db_column="TURTLE_ID", blank=True, null=True
    )  # Field name made lowercase.
    observation_id = models.IntegerField(
        db_column="OBSERVATION_ID", blank=True, null=True
    )  # Field name made lowercase.
    recapture_left_tag_id = models.CharField(
        db_column="RECAPTURE_LEFT_TAG_ID", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    recapture_right_tag_id = models.CharField(
        db_column="RECAPTURE_RIGHT_TAG_ID", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    recapture_left_tag_id_2 = models.CharField(
        db_column="RECAPTURE_LEFT_TAG_ID_2", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    recapture_right_tag_id_2 = models.CharField(
        db_column="RECAPTURE_RIGHT_TAG_ID_2", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    other_left_tag = models.CharField(
        db_column="OTHER_LEFT_TAG", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    other_right_tag = models.CharField(
        db_column="OTHER_RIGHT_TAG", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    new_left_tag_id = models.CharField(
        db_column="NEW_LEFT_TAG_ID", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    new_right_tag_id = models.CharField(
        db_column="NEW_RIGHT_TAG_ID", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    alive = models.CharField(
        db_column="ALIVE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    place_code = models.CharField(
        db_column="PLACE_CODE", max_length=4, blank=True, null=True
    )  # Field name made lowercase.
    observation_date = models.DateTimeField(
        db_column="OBSERVATION_DATE", blank=True, null=True
    )  # Field name made lowercase.
    observation_time = models.DateTimeField(
        db_column="OBSERVATION_TIME", blank=True, null=True
    )  # Field name made lowercase.
    nesting = models.CharField(
        db_column="NESTING", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    species_code = models.CharField(
        db_column="SPECIES_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    identification_confidence = models.CharField(
        db_column="IDENTIFICATION_CONFIDENCE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    sex = models.CharField(
        db_column="SEX", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    curved_carapace_length = models.IntegerField(
        db_column="CURVED_CARAPACE_LENGTH", blank=True, null=True
    )  # Field name made lowercase.
    curved_carapace_width = models.IntegerField(
        db_column="CURVED_CARAPACE_WIDTH", blank=True, null=True
    )  # Field name made lowercase.
    activity_code = models.CharField(
        db_column="ACTIVITY_CODE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    beach_position_code = models.CharField(
        db_column="BEACH_POSITION_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    damage_carapace = models.CharField(
        db_column="DAMAGE_CARAPACE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    damage_lff = models.CharField(
        db_column="DAMAGE_LFF", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    damage_rff = models.CharField(
        db_column="DAMAGE_RFF", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    damage_lhf = models.CharField(
        db_column="DAMAGE_LHF", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    damage_rhf = models.CharField(
        db_column="DAMAGE_RHF", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    clutch_completed = models.CharField(
        db_column="CLUTCH_COMPLETED", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    egg_count = models.IntegerField(
        db_column="EGG_COUNT", blank=True, null=True
    )  # Field name made lowercase.
    egg_count_method = models.CharField(
        db_column="EGG_COUNT_METHOD", max_length=3, blank=True, null=True
    )  # Field name made lowercase.
    measured_by = models.CharField(
        db_column="MEASURED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    recorded_by = models.CharField(
        db_column="RECORDED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    tagged_by = models.CharField(
        db_column="TAGGED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    measurement_type_1 = models.CharField(
        db_column="MEASUREMENT_TYPE_1", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    measurement_value_1 = models.FloatField(
        db_column="MEASUREMENT_VALUE_1", blank=True, null=True
    )  # Field name made lowercase.
    measurement_type_2 = models.CharField(
        db_column="MEASUREMENT_TYPE_2", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    measurement_value_2 = models.FloatField(
        db_column="MEASUREMENT_VALUE_2", blank=True, null=True
    )  # Field name made lowercase.
    datum_code = models.CharField(
        db_column="DATUM_CODE", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    latitude = models.FloatField(
        db_column="LATITUDE", blank=True, null=True
    )  # Field name made lowercase.
    longitude = models.FloatField(
        db_column="LONGITUDE", blank=True, null=True
    )  # Field name made lowercase.
    latitude_degrees = models.IntegerField(
        db_column="LATITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_minutes = models.FloatField(
        db_column="LATITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_seconds = models.FloatField(
        db_column="LATITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    longitude_degrees = models.IntegerField(
        db_column="LONGITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_minutes = models.FloatField(
        db_column="LONGITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_seconds = models.FloatField(
        db_column="LONGITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    zone = models.IntegerField(
        db_column="ZONE", blank=True, null=True
    )  # Field name made lowercase.
    easting = models.FloatField(
        db_column="EASTING", blank=True, null=True
    )  # Field name made lowercase.
    northing = models.FloatField(
        db_column="NORTHING", blank=True, null=True
    )  # Field name made lowercase.
    identification_type = models.CharField(
        db_column="IDENTIFICATION_TYPE", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    identifier = models.CharField(
        db_column="IDENTIFIER", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DATA_ENTRY_EXCEPTIONS"
        constraints = [
            models.UniqueConstraint(
                fields=["entry_batch_id", "data_entry_id"],
                name="unique_entry_batch_data_entry"
            )
        ]


class TrtDataEntryPersons(models.Model):
    data_entry_person_id = models.AutoField(
        db_column="DATA_ENTRY_PERSON_ID", primary_key=True
    )  # Field name made lowercase.
    entry_batch = models.ForeignKey(
        "TrtEntryBatches", models.CASCADE, db_column="ENTRY_BATCH_ID"
    )  # Field name made lowercase.
    person_name = models.CharField(
        db_column="PERSON_NAME", max_length=100
    )  # Field name made lowercase.
    person_id = models.IntegerField(
        db_column="PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DATA_ENTRY_PERSONS"
        constraints = [
            models.UniqueConstraint(
                fields=["entry_batch", "person_name"],
                name="unique_entry_batch_person"
            )
        ]

    # def __str__(self):
    #     return f"{self.person_name}"


class TrtDatumCodes(models.Model):
    datum_code = models.CharField(
        db_column="DATUM_CODE", primary_key=True, max_length=5
    )  # Field name made lowercase.
    datum_description = models.CharField(
        db_column="DATUM_DESCRIPTION", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    semi_major_axis = models.FloatField(
        db_column="SEMI_MAJOR_AXIS", blank=True, null=True
    )  # Field name made lowercase.
    inverse_flattening = models.FloatField(
        db_column="INVERSE_FLATTENING", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DATUM_CODES"


class TrtDefault(models.Model):
    id = models.CharField(
        db_column="ID", primary_key=True, max_length=10
    )  # Field name made lowercase.
    dataentry_exportpath = models.CharField(
        db_column="DataEntry_ExportPath", max_length=200
    )  # Field name made lowercase.
    dataentry_sourcedatabase = models.CharField(
        db_column="DataEntry_SourceDatabase", max_length=200, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DEFAULT"


class TrtDocuments(models.Model):
    document_id = models.AutoField(
        db_column="DOCUMENT_ID", primary_key=True
    )  # Field name made lowercase.
    document_type = models.CharField(
        db_column="DOCUMENT_TYPE", max_length=10
    )  # Field name made lowercase.
    filename = models.CharField(
        db_column="FILENAME", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    turtle_id = models.IntegerField(
        db_column="TURTLE_ID", blank=True, null=True
    )  # Field name made lowercase.
    person_id = models.IntegerField(
        db_column="PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.
    species_code = models.CharField(
        db_column="SPECIES_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    title = models.CharField(
        db_column="TITLE", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DOCUMENTS"


class TrtDocumentTypes(models.Model):
    document_type = models.CharField(
        db_column="DOCUMENT_TYPE", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_DOCUMENT_TYPES"


class TrtEggCountMethods(models.Model):
    egg_count_method = models.CharField(
        db_column="EGG_COUNT_METHOD", primary_key=True, max_length=3
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_EGG_COUNT_METHODS"
    def __str__(self):
        return f"{self.description}"


class TrtEntryBatches(models.Model):
    entry_batch_id = models.AutoField(
        db_column="ENTRY_BATCH_ID", primary_key=True
    )  # Field name made lowercase.
    entry_date = models.DateTimeField(
        db_column="ENTRY_DATE", blank=True, null=True
    )  # Field name made lowercase.
    entered_person_id = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="ENTERED_PERSON_ID",
        blank=True,
        null=True,
    )  # fake foreign key #models.IntegerField(db_column='ENTERED_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(
        db_column="FILENAME", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    pr_date_convention = models.BooleanField(
        db_column="PR_DATE_CONVENTION",default=False
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_ENTRY_BATCHES"
        verbose_name = "Entry Batch"
        verbose_name_plural = "Entry Batches"
        ordering = ["entry_batch_id"]

    def __str__(self):
        return f"{self.entry_batch_id}"


class TrtIdentification(models.Model):
    turtle = models.OneToOneField(
        "TrtTurtles", models.CASCADE, db_column="TURTLE_ID", primary_key=True
    )  # Field name made lowercase.
    identification_type = models.ForeignKey(
        "TrtIdentificationTypes",
        models.CASCADE,
        db_column="IDENTIFICATION_TYPE",
        related_name="identification_type2",
    )  # Field name made lowercase.
    identifier = models.CharField(
        db_column="IDENTIFIER", max_length=20
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_IDENTIFICATION"
        constraints = [
            models.UniqueConstraint(
                fields=["turtle", "identification_type", "identifier"],
                name="unique_turtle_identification"
            )
        ]


class TrtIdentificationTypes(models.Model):
    identification_type = models.CharField(
        db_column="IDENTIFICATION_TYPE", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_IDENTIFICATION_TYPES"
    def __str__(self):
        return f"{self.description}"
    


class TrtLocations(models.Model):
    location_code = models.CharField(
        db_column="LOCATION_CODE", primary_key=True, max_length=2
    )  # Field name made lowercase.
    location_name = models.CharField(
        db_column="LOCATION_NAME", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_LOCATIONS"

    def __str__(self):
        return f"{self.location_name}"


class TrtMeasurements(models.Model):
    id = models.AutoField(db_column="ID", primary_key=True)
    observation = models.ForeignKey(
        "TrtObservations", on_delete=models.CASCADE
    )  # Field name made lowercase.
    measurement_type = models.ForeignKey(
        "TrtMeasurementTypes", models.CASCADE, db_column="MEASUREMENT_TYPE"
    )  # Field name made lowercase.
    measurement_value = models.FloatField(
        db_column="MEASUREMENT_VALUE"
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_MEASUREMENTS"
        constraints = [
            models.UniqueConstraint(
                fields=["observation", "measurement_type"],
                name="unique_observation_measurement_type"
            )
        ]


class TrtMeasurementTypes(models.Model):
    measurement_type = models.CharField(
        db_column="MEASUREMENT_TYPE", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=100
    )  # Field name made lowercase.
    measurement_units = models.CharField(
        db_column="MEASUREMENT_UNITS", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    minimum_value = models.FloatField(
        db_column="MINIMUM_VALUE", blank=True, null=True
    )  # Field name made lowercase.
    maximum_value = models.FloatField(
        db_column="MAXIMUM_VALUE", blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_MEASUREMENT_TYPES"

    def __str__(self):
        return f"{self.description}"


class TrtNesting(models.Model):
    place_code = models.CharField(
        db_column="PLACE_CODE", primary_key=True, max_length=4
    )  # Field name made lowercase.
    species_code = models.CharField(
        db_column="SPECIES_CODE", max_length=2
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_NESTING"
        constraints = [
            models.UniqueConstraint(
                fields=["place_code", "species_code"],
                name="unique_place_species"
            )
        ]


class TrtNestingSeason(models.Model):
    nesting_seasonid = models.AutoField(
        db_column="NESTING_SEASONID", primary_key=True
    )  # Field name made lowercase.
    nesting_season = models.CharField(
        db_column="NESTING_SEASON", max_length=20
    )  # Field name made lowercase.
    startdate = models.DateTimeField(
        db_column="STARTDATE"
    )  # Field name made lowercase.
    enddate = models.DateTimeField(db_column="ENDDATE")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_NESTING_SEASON"


class TrtObservations(models.Model):
    observation_id = models.AutoField(
        db_column="OBSERVATION_ID", primary_key=True
    )  # Field name made lowercase.
    turtle = models.ForeignKey(
        "TrtTurtles", models.CASCADE, db_column="TURTLE_ID"
    )  # Field name made lowercase.
    observation_date = models.DateTimeField(
        db_column="OBSERVATION_DATE"
    )  # Field name made lowercase.
    observation_time = models.DateTimeField(
        db_column="OBSERVATION_TIME", blank=True, null=True
    )  # Field name made lowercase.
    observation_date_old = models.DateTimeField(
        db_column="OBSERVATION_DATE_OLD", blank=True, null=True
    )  # Field name made lowercase.
    alive = models.ForeignKey(
        "TrtYesNo", models.SET_NULL, db_column="ALIVE", blank=True, null=True
    )  # fake foreign key #models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    measurer_person = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="MEASURER_PERSON_ID",
        blank=True,
        null=True,
        related_name="measurer_person",
    )  # Field name made lowercase.
    measurer_reporter_person = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="MEASURER_REPORTER_PERSON_ID",
        blank=True,
        null=True,
        related_name="measurer_reporter_person",
    )  # Field name made lowercase.
    tagger_person = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="TAGGER_PERSON_ID",
        blank=True,
        null=True,
        related_name="tagger_person",
    )  # Field name made lowercase.
    reporter_person = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="REPORTER_PERSON_ID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    place_code = models.ForeignKey(
        "TrtPlaces", models.SET_NULL, db_column="PLACE_CODE", blank=True, null=True
    )  # Field name made lowercase.
    place_description = models.CharField(
        db_column="PLACE_DESCRIPTION", max_length=300, blank=True, null=True
    )  # Field name made lowercase.
    datum_code = models.ForeignKey(
        TrtDatumCodes, models.SET_NULL, db_column="DATUM_CODE", blank=True, null=True
    )  # Field name made lowercase.
    latitude = models.FloatField(
        db_column="LATITUDE", blank=True, null=True
    )  # Field name made lowercase.
    longitude = models.FloatField(
        db_column="LONGITUDE", blank=True, null=True
    )  # Field name made lowercase.
    latitude_degrees = models.IntegerField(
        db_column="LATITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_minutes = models.FloatField(
        db_column="LATITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    latitude_seconds = models.FloatField(
        db_column="LATITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    longitude_degrees = models.IntegerField(
        db_column="LONGITUDE_DEGREES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_minutes = models.FloatField(
        db_column="LONGITUDE_MINUTES", blank=True, null=True
    )  # Field name made lowercase.
    longitude_seconds = models.FloatField(
        db_column="LONGITUDE_SECONDS", blank=True, null=True
    )  # Field name made lowercase.
    zone = models.IntegerField(
        db_column="ZONE", blank=True, null=True
    )  # Field name made lowercase.
    easting = models.FloatField(
        db_column="EASTING", blank=True, null=True
    )  # Field name made lowercase.
    northing = models.FloatField(
        db_column="NORTHING", blank=True, null=True
    )  # Field name made lowercase.
    activity_code = models.ForeignKey(
        TrtActivities, models.SET_NULL, db_column="ACTIVITY_CODE", blank=True, null=True
    )  # Field name made lowercase.
    beach_position_code = models.ForeignKey(
        TrtBeachPositions,
        models.SET_NULL,
        db_column="BEACH_POSITION_CODE",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    condition_code = models.ForeignKey(
        TrtConditionCodes,
        models.SET_NULL,
        db_column="CONDITION_CODE",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    nesting = models.ForeignKey(
        "TrtYesNo",
        models.SET_NULL,
        db_column="NESTING",
        blank=True,
        null=True,
        related_name="nestingobs",
    )  # fake foreign key #models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)  # Field name made lowercase.
    clutch_completed = models.CharField(
        db_column="CLUTCH_COMPLETED", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    number_of_eggs = models.SmallIntegerField(
        db_column="NUMBER_OF_EGGS", blank=True, null=True
    )  # Field name made lowercase.
    egg_count_method = models.ForeignKey(
        TrtEggCountMethods,
        models.SET_NULL,
        db_column="EGG_COUNT_METHOD",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    measurements = models.CharField(
        db_column="MEASUREMENTS", max_length=1
    )  # Field name made lowercase.
    action_taken = models.CharField(
        db_column="ACTION_TAKEN", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.TextField(
        db_column="COMMENTS", blank=True, null=True
    )  # Field name made lowercase.
    entered_by = models.CharField(
        db_column="ENTERED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    date_entered = models.DateTimeField(
        db_column="DATE_ENTERED", blank=True, null=True
    )  # Field name made lowercase.
    original_observation_id = models.IntegerField(
        db_column="ORIGINAL_OBSERVATION_ID", blank=True, null=True
    )  # Field name made lowercase.
    entry_batch = models.ForeignKey(
        TrtEntryBatches,
        models.SET_NULL,
        db_column="ENTRY_BATCH_ID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    comment_fromrecordedtagstable = models.TextField(
        db_column="COMMENT_FROMRECORDEDTAGSTABLE", blank=True, null=True
    )  # Field name made lowercase.
    scars_left = models.BooleanField(
        db_column="SCARS_LEFT"
    )  # Field name made lowercase.
    scars_right = models.BooleanField(
        db_column="SCARS_RIGHT"
    )  # Field name made lowercase.
    other_tags = models.CharField(
        db_column="OTHER_TAGS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    other_tags_identification_type = models.ForeignKey(
        TrtIdentificationTypes,
        models.SET_NULL,
        db_column="OTHER_TAGS_IDENTIFICATION_TYPE",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    transferid = models.IntegerField(
        db_column="TransferID", blank=True, null=True
    )  # Field name made lowercase.
    mund = models.BooleanField(db_column="Mund")  # Field name made lowercase.
    entered_by_person = models.ForeignKey(
        "TrtPersons",
        models.SET_NULL,
        db_column="ENTERED_BY_PERSON_ID",
        blank=True,
        null=True,
        related_name="entered_by_person",
    )  # Field name made lowercase.
    scars_left_scale_1 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_1"
    )  # Field name made lowercase.
    scars_left_scale_2 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_2"
    )  # Field name made lowercase.
    scars_left_scale_3 = models.BooleanField(
        db_column="SCARS_LEFT_SCALE_3"
    )  # Field name made lowercase.
    scars_right_scale_1 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_1"
    )  # Field name made lowercase.
    scars_right_scale_2 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_2"
    )  # Field name made lowercase.
    scars_right_scale_3 = models.BooleanField(
        db_column="SCARS_RIGHT_SCALE_3"
    )  # Field name made lowercase.
    cc_length_not_measured = models.BooleanField(
        db_column="CC_LENGTH_Not_Measured"
    )  # Field name made lowercase.
    cc_notch_length_not_measured = models.BooleanField(
        db_column="CC_NOTCH_LENGTH_Not_Measured"
    )  # Field name made lowercase.
    cc_width_not_measured = models.BooleanField(
        db_column="CC_WIDTH_Not_Measured"
    )  # Field name made lowercase.
    tagscarnotchecked = models.BooleanField(
        db_column="TagScarNotChecked"
    )  # Field name made lowercase.
    didnotcheckforinjury = models.BooleanField(
        db_column="DidNotCheckForInjury"
    )  # Field name made lowercase.
    date_convention = models.CharField(
        db_column="DATE_CONVENTION", max_length=1
    )  # Field name made lowercase.
    observation_status = models.CharField(
        db_column="OBSERVATION_STATUS", max_length=50, blank=True, null=True, editable=False
    )  # Field name made lowercase.
    corrected_date = models.DateTimeField(
        db_column="CORRECTED_DATE", blank=True, null=True, editable=False
    )  # Field name made lowercase.
    dud_filpper_tag = models.CharField(
        max_length=10, 
        db_column="DUD_FLIPPER_TAG",
        blank=True,
        null=True,
    )  
    dud_filpper_tag_2 = models.CharField(
        max_length=10,
        db_column="DUD_FLIPPER_TAG_2",
        blank=True,
        null=True,
    )
    dud_pit_tag = models.CharField(
        max_length=50,
        db_column="DUD_PIT_TAG",
        blank=True,
        null=True,
    )
    dud_pit_tag_2 = models.CharField(
        max_length=50,
        db_column="DUD_PIT_TAG_2",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "TRT_OBSERVATIONS"
        constraints = [
            models.UniqueConstraint(
                fields=["observation_id", "turtle"],
                name="unique_observation_id_turtle"
            )
        ]
        verbose_name = "Observation"
        verbose_name_plural = "Observations"

    def __str__(self):
        return f"{self.observation_date}"
    
    def save(self, *args, **kwargs):
        if 'observation_status' in self.__dict__:
            del self.__dict__['observation_status']
        if 'corrected_date' in self.__dict__:
            del self.__dict__['corrected_date']
        super().save(*args, **kwargs)


class TrtPersons(models.Model):
    person_id = models.AutoField(
        db_column="PERSON_ID", primary_key=True
    )  # Field name made lowercase.
    first_name = models.CharField(
        db_column="FIRST_NAME", max_length=50, db_index=True
    )  # Field name made lowercase.
    middle_name = models.CharField(
        db_column="MIDDLE_NAME", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    surname = models.CharField(
        db_column="SURNAME", max_length=50, blank=True, null=True, db_index=True
    )  # Field name made lowercase.
    specialty = models.CharField(
        db_column="SPECIALTY", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    address_line_1 = models.CharField(
        db_column="ADDRESS_LINE_1", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    address_line_2 = models.CharField(
        db_column="ADDRESS_LINE_2", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    town = models.CharField(
        db_column="TOWN", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    state = models.CharField(
        db_column="STATE", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    post_code = models.CharField(
        db_column="POST_CODE", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    country = models.CharField(
        db_column="COUNTRY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    telephone = models.CharField(
        db_column="TELEPHONE", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    fax = models.CharField(
        db_column="FAX", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    mobile = models.CharField(
        db_column="MOBILE", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    email = models.CharField(
        db_column="EMAIL", max_length=150, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=400, blank=True, null=True
    )  # Field name made lowercase.
    transfer = models.CharField(
        db_column="Transfer", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    recorder = models.BooleanField(db_column="Recorder")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_PERSONS"
        ordering = ["first_name", "surname"]
        verbose_name = "Person"
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.first_name} {self.surname}"


class TrtPitTags(models.Model):
    pittag_id = models.CharField(
        db_column="PIT_TAG_ID", primary_key=True, max_length=50
    )  # Field name made lowercase.
    issue_location = models.CharField(
        db_column="ISSUE_LOCATION", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    custodian_person_id = models.IntegerField(
        db_column="CUSTODIAN_PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.
    turtle = models.ForeignKey(
        "TrtTurtles", models.SET_NULL, db_column="TURTLE_ID", blank=True, null=True
    )  # Field name made lowercase.
    pit_tag_status = models.ForeignKey(
        "TrtPitTagStatus",
        models.SET_NULL,
        db_column="PIT_TAG_STATUS",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    return_date = models.DateTimeField(
        db_column="RETURN_DATE", blank=True, null=True
    )  # Field name made lowercase.
    return_condition = models.CharField(
        db_column="RETURN_CONDITION", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    field_person_id = models.IntegerField(
        db_column="FIELD_PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.
    tag_order_id = models.IntegerField(
        db_column="TAG_ORDER_ID", blank=True, null=True
    )  # Field name made lowercase.
    batch_number = models.CharField(
        db_column="BATCH_NUMBER", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    box_number = models.CharField(
        db_column="BOX_NUMBER", max_length=50, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_PIT_TAGS"
        constraints = [
            models.UniqueConstraint(
                fields=["pittag_id", "turtle"],
                name="unique_pittag_id_turtle"
            )
        ]
        verbose_name = "Pit tag"
        verbose_name_plural = "Pit tags"
        ordering = ["pittag_id"]

    def __str__(self):
        return f"{self.pittag_id}"


class TrtPitTagStates(models.Model):
    pit_tag_state = models.CharField(
        db_column="PIT_TAG_STATE", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    pit_tag_status = models.ForeignKey(
        "TrtPitTagStatus", models.CASCADE, db_column="PIT_TAG_STATUS"
    )  # Field name made lowercase.
    existing_tag_list = models.BooleanField(
        db_column="EXISTING_TAG_LIST"
    )  # Field name made lowercase.
    new_tag_list = models.BooleanField(
        db_column="NEW_TAG_LIST"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_PIT_TAG_STATES"


class TrtPitTagStatus(models.Model):
    pit_tag_status = models.CharField(
        db_column="PIT_TAG_STATUS", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_PIT_TAG_STATUS"

    def __str__(self):
        return f"{self.description}"


class TrtPlaces(models.Model):
    place_code = models.CharField(
        db_column="PLACE_CODE", primary_key=True, max_length=4
    )  # Field name made lowercase.
    place_name = models.CharField(
        db_column="PLACE_NAME", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    location_code = models.ForeignKey(
        "TrtLocations", models.DO_NOTHING, db_column="LOCATION_CODE"
    )  # fake foreign key #models.CharField(db_column='LOCATION_CODE', max_length=2)  # Field name made lowercase.
    rookery = models.CharField(
        db_column="ROOKERY", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    beach_approach = models.CharField(
        db_column="BEACH_APPROACH", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    aspect = models.CharField(
        db_column="ASPECT", max_length=3, blank=True, null=True
    )  # Field name made lowercase.
    datum_code = models.CharField(
        db_column="DATUM_CODE", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    latitude = models.FloatField(
        db_column="LATITUDE", blank=True, null=True
    )  # Field name made lowercase.
    longitude = models.FloatField(
        db_column="LONGITUDE", blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_PLACES"
        ordering = ["place_name"]

    def get_full_name(self):
        return f"{self.location_code} - {self.place_name}"
    
    def __str__(self):
        return self.place_code


class TrtRecordedIdentification(models.Model):
    recorded_identification_id = models.AutoField(
        db_column="RECORDED_IDENTIFICATION_ID", primary_key=True
    )  # Field name made lowercase.
    observation_id = models.IntegerField(
        db_column="OBSERVATION_ID"
    )  # Field name made lowercase.
    turtle = models.ForeignKey(
        TrtIdentification, models.CASCADE, db_column="TURTLE_ID", related_name="turtle2"
    )  # Field name made lowercase.
    identification_type = models.ForeignKey(
        TrtIdentification, models.CASCADE, db_column="IDENTIFICATION_TYPE"
    )  # Field name made lowercase.
    identifier = models.ForeignKey(
        TrtIdentification,
        models.CASCADE,
        db_column="IDENTIFIER",
        related_name="identifier2",
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_RECORDED_IDENTIFICATION"


class TrtRecordedPitTags(models.Model):
    recorded_pittag_id = models.AutoField(
        db_column="RECORDED_PIT_TAG_ID", primary_key=True
    )  # Field name made lowercase.
    observation_id = models.ForeignKey(
        "TrtObservations",
        models.CASCADE,
        db_column="OBSERVATION_ID",
        blank=True,
        null=True,
    )  # fake foreign key #models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
    pittag_id = models.ForeignKey(
        "TrtPitTags", models.CASCADE, db_column="PIT_TAG_ID", blank=True, null=True
    )  # fake foreign key #models.CharField(db_column='pittag_id', max_length=50)  # Field name made lowercase.
    pit_tag_state = models.ForeignKey(
        TrtPitTagStates, models.DO_NOTHING, db_column="PIT_TAG_STATE"
    )  # Field name made lowercase.
    pit_tag_position = models.CharField(
        db_column="PIT_TAG_POSITION", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    turtle_id = models.ForeignKey(
        "TrtTurtles",
        on_delete=models.CASCADE,
        db_column="TURTLE_ID",
        related_name="recorded_pittags",)  # Field name made lowercase.
    checked = models.BooleanField(db_column="Checked")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_RECORDED_PIT_TAGS"


class TrtRecordedTags(models.Model):
    recorded_tag_id = models.AutoField(
        db_column="RECORDED_TAG_ID", primary_key=True
    )  # Field name made lowercase.
    observation_id = models.ForeignKey(
        "TrtObservations",
        models.CASCADE,
        db_column="OBSERVATION_ID",
        blank=True,
        null=True,
    )  # fake foreign key #models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
    tag_id = models.ForeignKey(
        "TrtTags", models.CASCADE, db_column="TAG_ID", blank=True, null=True
    )  # fake foreign key #models.CharField(db_column='TAG_ID', max_length=10)  # Field name made lowercase.
    other_tag_id = models.CharField(
        db_column="OTHER_TAG_ID", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    side = models.CharField(
        db_column="SIDE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    tag_state = models.CharField(
        db_column="TAG_STATE", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    tag_position = models.SmallIntegerField(
        db_column="TAG_POSITION", blank=True, null=True
    )  # Field name made lowercase.
    barnacles = models.BooleanField(db_column="BARNACLES")  # Field name made lowercase.
    turtle_id = models.IntegerField(db_column="TURTLE_ID")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_RECORDED_TAGS"


class TrtSamples(models.Model):
    sample_id = models.AutoField(
        db_column="SAMPLE_ID", primary_key=True
    )  # Field name made lowercase.
    turtle = models.ForeignKey(
        "TrtTurtles", models.CASCADE, db_column="TURTLE_ID"
    )  # Field name made lowercase.
    sample_date = models.DateTimeField(
        db_column="SAMPLE_DATE", blank=True, null=True
    )  # Field name made lowercase.
    tissue_type = models.ForeignKey(
        "TrtTissueTypes", models.CASCADE, db_column="TISSUE_TYPE"
    )  # Field name made lowercase.
    arsenic = models.FloatField(
        db_column="ARSENIC", blank=True, null=True
    )  # Field name made lowercase.
    selenium = models.FloatField(
        db_column="SELENIUM", blank=True, null=True
    )  # Field name made lowercase.
    zinc = models.FloatField(
        db_column="ZINC", blank=True, null=True
    )  # Field name made lowercase.
    cadmium = models.FloatField(
        db_column="CADMIUM", blank=True, null=True
    )  # Field name made lowercase.
    copper = models.FloatField(
        db_column="COPPER", blank=True, null=True
    )  # Field name made lowercase.
    lead = models.FloatField(
        db_column="LEAD", blank=True, null=True
    )  # Field name made lowercase.
    mercury = models.FloatField(
        db_column="MERCURY", blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    observation_id = models.IntegerField(
        db_column="OBSERVATION_ID", blank=True, null=True
    )  # Field name made lowercase.
    sample_label = models.CharField(
        db_column="SAMPLE_LABEL", max_length=50, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_SAMPLES"


class TrtSighting(models.Model):
    sightingid = models.AutoField(
        db_column="SIGHTINGID", primary_key=True
    )  # Field name made lowercase.
    observation_time = models.DateTimeField(
        db_column="OBSERVATION_TIME", blank=True, null=True
    )  # Field name made lowercase.
    observation_date = models.DateTimeField(
        db_column="OBSERVATION_DATE", blank=True, null=True
    )  # Field name made lowercase.
    alive = models.CharField(
        db_column="ALIVE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    species_code = models.CharField(
        db_column="SPECIES_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    sex = models.CharField(
        db_column="SEX", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    location_code = models.CharField(
        db_column="LOCATION_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    turtle_status = models.CharField(
        db_column="TURTLE_STATUS", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    place_code = models.CharField(
        db_column="PLACE_CODE", max_length=4, blank=True, null=True
    )  # Field name made lowercase.
    activity_code = models.CharField(
        db_column="ACTIVITY_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    beach_position_code = models.CharField(
        db_column="BEACH_POSITION_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    datum_code = models.CharField(
        db_column="DATUM_CODE", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    latitude = models.CharField(
        db_column="LATITUDE", max_length=7, blank=True, null=True
    )  # Field name made lowercase.
    longitude = models.FloatField(
        db_column="LONGITUDE", blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    entered_by_person_id = models.IntegerField(
        db_column="ENTERED_BY_PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_SIGHTING"


class TrtSpecies(models.Model):
    species_code = models.CharField(
        db_column="SPECIES_CODE", primary_key=True, max_length=2
    )  # Field name made lowercase.
    scientific_name = models.CharField(
        db_column="SCIENTIFIC_NAME", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    common_name = models.CharField(
        db_column="COMMON_NAME", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    old_species_code = models.CharField(
        db_column="OLD_SPECIES_CODE", max_length=2, blank=True, null=True
    )  # Field name made lowercase.
    hide_dataentry = models.BooleanField(
        db_column="Hide_DataEntry"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_SPECIES"

    def __str__(self):
        return f"{self.common_name}"


class TrtTags(models.Model):
    tag_id = models.CharField(
        db_column="TAG_ID", primary_key=True, max_length=10
    )  # Field name made lowercase.
    tag_order_id = models.IntegerField(
        db_column="TAG_ORDER_ID", blank=True, null=True
    )  # Field name made lowercase.
    issue_location = models.CharField(
        db_column="ISSUE_LOCATION", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    custodian_person_id = models.IntegerField(
        db_column="CUSTODIAN_PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.
    turtle = models.ForeignKey(
        "TrtTurtles", models.SET_NULL, db_column="TURTLE_ID", blank=True, null=True
    )  # Field name made lowercase.
    side = models.CharField(
        db_column="SIDE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    tag_status = models.ForeignKey(
        "TrtTagStatus", models.SET_NULL, db_column="TAG_STATUS", blank=True, null=True
    )  # Field name made lowercase.
    return_date = models.DateTimeField(
        db_column="RETURN_DATE", blank=True, null=True
    )  # Field name made lowercase.
    return_condition = models.CharField(
        db_column="RETURN_CONDITION", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    field_person_id = models.IntegerField(
        db_column="FIELD_PERSON_ID", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TAGS"
        constraints = [
            models.UniqueConstraint(
                fields=["tag_id", "turtle"],
                name="unique_tag_id_turtle"
            )
        ]
        verbose_name = "Flipper tag"
        verbose_name_plural = "Flipper tags"
        ordering = [
            "tag_id",
        ]

    def __str__(self):
        return f"{self.tag_id}"


class TrtTagOrders(models.Model):
    tag_order_id = models.AutoField(
        db_column="TAG_ORDER_ID", primary_key=True
    )  # Field name made lowercase.
    order_date = models.DateTimeField(
        db_column="ORDER_DATE", blank=True, null=True
    )  # Field name made lowercase.
    order_number = models.CharField(
        db_column="ORDER_NUMBER", max_length=20
    )  # Field name made lowercase.
    tag_prefix = models.CharField(
        db_column="TAG_PREFIX", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    start_tag_number = models.IntegerField(
        db_column="START_TAG_NUMBER", blank=True, null=True
    )  # Field name made lowercase.
    end_tag_number = models.IntegerField(
        db_column="END_TAG_NUMBER", blank=True, null=True
    )  # Field name made lowercase.
    total_tags = models.SmallIntegerField(
        db_column="TOTAL_TAGS", blank=True, null=True
    )  # Field name made lowercase.
    date_received = models.DateTimeField(
        db_column="DATE_RECEIVED", blank=True, null=True
    )  # Field name made lowercase.
    paid_by = models.CharField(
        db_column="PAID_BY", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TAG_ORDERS"
        verbose_name = "Tag Order"  # Singular name for one object
        verbose_name_plural = "Tag Orders"

    def __str__(self):
        return f"{self.tag_order_id}"


class TrtTagStates(models.Model):
    tag_state = models.CharField(
        db_column="TAG_STATE", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.
    tag_status = models.CharField(
        db_column="TAG_STATUS", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    existing_tag_list = models.BooleanField(
        db_column="EXISTING_TAG_LIST"
    )  # Field name made lowercase.
    new_tag_list = models.BooleanField(
        db_column="NEW_TAG_LIST"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TAG_STATES"

    def __str__(self):
        return f"{self.description}"


class TrtTagStatus(models.Model):
    tag_status = models.CharField(
        db_column="TAG_STATUS", primary_key=True, max_length=10
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TAG_STATUS"

    def __str__(self):
        return f"{self.description}"


class TrtTissueTypes(models.Model):
    tissue_type = models.CharField(
        db_column="TISSUE_TYPE", primary_key=True, max_length=5
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=50
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TISSUE_TYPES"
        
    def __str__(self):
        return self.description


class TrtTurtles(models.Model):
    turtle_id = models.AutoField(
        db_column="TURTLE_ID", primary_key=True
    )  # models.IntegerField(db_column='TURTLE_ID', primary_key=True)  # Field name made lowercase.
    species_code = models.ForeignKey(
        TrtSpecies, models.DO_NOTHING, db_column="SPECIES_CODE"
    )  # Field name made lowercase.
    identification_confidence = models.CharField(
        db_column="IDENTIFICATION_CONFIDENCE", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    sex = models.CharField(db_column="SEX", max_length=1)  # Field name made lowercase.
    turtle_status = models.ForeignKey(
        "TrtTurtleStatus",
        models.SET_NULL,
        db_column="TURTLE_STATUS",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    location_code = models.ForeignKey(
        TrtLocations, models.SET_NULL, db_column="LOCATION_CODE", blank=True, null=True
    )  # Field name made lowercase.
    cause_of_death = models.ForeignKey(
        TrtCauseOfDeath,
        models.SET_NULL,
        db_column="CAUSE_OF_DEATH",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    re_entered_population = models.CharField(
        db_column="RE_ENTERED_POPULATION", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    comments = models.CharField(
        db_column="COMMENTS", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    entered_by = models.CharField(
        db_column="ENTERED_BY", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    date_entered = models.DateTimeField(
        db_column="DATE_ENTERED", blank=True, null=True
    )  # Field name made lowercase.
    original_turtle_id = models.IntegerField(
        db_column="ORIGINAL_TURTLE_ID", blank=True, null=True
    )  # Field name made lowercase.
    entry_batch_id = models.IntegerField(
        db_column="ENTRY_BATCH_ID", blank=True, null=True
    )  # Field name made lowercase.
    tag = models.CharField(
        db_column="Tag", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    mund_id = models.CharField(
        db_column="Mund_ID", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    turtle_name = models.CharField(
        db_column="TURTLE_NAME", max_length=50, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TURTLES"
        verbose_name = "Turtle"
        verbose_name_plural = "Turtles"
        ordering = ["turtle_id"]

    def __str__(self):
        return f"{self.turtle_id}"

    def get_tags_description(self):
        """Returns a comma-separated list of tag serial numbers for this turtle."""
        tags = []
        for tag in self.trttags_set.all():
            tags.append(str(tag))
        for tag in self.trtpittags_set.all():
            tags.append(str(tag))
        return ", ".join(tags)


class TrtTurtleStatus(models.Model):
    turtle_status = models.CharField(
        db_column="TURTLE_STATUS", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=100
    )  # Field name made lowercase.
    new_tag_list = models.BooleanField(
        db_column="NEW_TAG_LIST"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_TURTLE_STATUS"

    def __str__(self):
        return f"{self.description}"


class TrtYesNo(models.Model):
    code = models.CharField(
        db_column="CODE", primary_key=True, max_length=1
    )  # Field name made lowercase.
    description = models.CharField(
        db_column="DESCRIPTION", max_length=10
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "TRT_YES_NO"

    def __str__(self):
        return f"{self.description}"

SEX_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("I", "Indeterminate"),
]
class Template(models.Model):
    template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location_code = models.CharField(max_length=50)
    place_code = models.CharField(max_length=50)
    species_code = models.CharField(max_length=50)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    class Meta:
        db_table = 'TRT_TEMPLATE'
        
    def __str__(self):
        return self.name

# class Tbldamage(models.Model):
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
#     body_part = models.CharField(db_column='BODY_PART', max_length=1)  # Field name made lowercase.
#     damage_code = models.CharField(db_column='DAMAGE_CODE', max_length=1)  # Field name made lowercase.
#     damage_cause_code = models.CharField(db_column='DAMAGE_CAUSE_CODE', max_length=2, blank=True, null=True)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblDamage'


# class TblimportEntryBatchId(models.Model):
#     entry_batch_id = models.IntegerField(db_column='ENTRY_BATCH_ID', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblImport_Entry_Batch_ID'


# class TblimportObservationid(models.Model):
#     obs_observation_id = models.IntegerField(db_column='Obs_OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.
#     admin_observation_id = models.IntegerField(db_column='Admin_OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblImport_ObservationID'


# class TblimportPersonid(models.Model):
#     obs_person_id = models.IntegerField(db_column='Obs_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     admin_person_id = models.IntegerField(db_column='Admin_PERSON_ID', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblImport_PersonID'


# class TblimportTurtleid(models.Model):
#     obs_turtle_id = models.IntegerField(db_column='Obs_TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
#     admin_turtle_id = models.IntegerField(db_column='Admin_TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
#     newturtle = models.BooleanField(db_column='NewTurtle')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblImport_TurtleID'


# class Tblmeasurements(models.Model):
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
#     measurement_type = models.CharField(db_column='MEASUREMENT_TYPE', max_length=10)  # Field name made lowercase.
#     measurement_value = models.FloatField(db_column='MEASUREMENT_VALUE')  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblMeasurements'


# class Tblobservations(models.Model):
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
#     turtle_id = models.IntegerField(db_column='TURTLE_ID')  # Field name made lowercase.
#     observation_date_old = models.DateTimeField(db_column='OBSERVATION_DATE_OLD', blank=True, null=True)  # Field name made lowercase.
#     observation_date = models.DateTimeField(db_column='OBSERVATION_DATE')  # Field name made lowercase.
#     observation_time = models.DateTimeField(db_column='OBSERVATION_TIME', blank=True, null=True)  # Field name made lowercase.
#     alive = models.CharField(db_column='ALIVE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     measurer_person_id = models.IntegerField(db_column='MEASURER_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     tagger_person_id = models.IntegerField(db_column='TAGGER_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     reporter_person_id = models.IntegerField(db_column='REPORTER_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     measurer_reporter_person_id = models.IntegerField(db_column='MEASURER_REPORTER_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     place_code = models.CharField(db_column='PLACE_CODE', max_length=4, blank=True, null=True)  # Field name made lowercase.
#     place_description = models.CharField(db_column='PLACE_DESCRIPTION', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     datum_code = models.CharField(db_column='DATUM_CODE', max_length=5, blank=True, null=True)  # Field name made lowercase.
#     latitude = models.FloatField(db_column='LATITUDE', blank=True, null=True)  # Field name made lowercase.
#     longitude = models.FloatField(db_column='LONGITUDE', blank=True, null=True)  # Field name made lowercase.
#     latitude_degrees = models.IntegerField(db_column='LATITUDE_DEGREES', blank=True, null=True)  # Field name made lowercase.
#     latitude_minutes = models.FloatField(db_column='LATITUDE_MINUTES', blank=True, null=True)  # Field name made lowercase.
#     latitude_seconds = models.FloatField(db_column='LATITUDE_SECONDS', blank=True, null=True)  # Field name made lowercase.
#     longitude_degrees = models.IntegerField(db_column='LONGITUDE_DEGREES', blank=True, null=True)  # Field name made lowercase.
#     longitude_minutes = models.FloatField(db_column='LONGITUDE_MINUTES', blank=True, null=True)  # Field name made lowercase.
#     longitude_seconds = models.FloatField(db_column='LONGITUDE_SECONDS', blank=True, null=True)  # Field name made lowercase.
#     zone = models.IntegerField(db_column='ZONE', blank=True, null=True)  # Field name made lowercase.
#     easting = models.FloatField(db_column='EASTING', blank=True, null=True)  # Field name made lowercase.
#     northing = models.FloatField(db_column='NORTHING', blank=True, null=True)  # Field name made lowercase.
#     activity_code = models.CharField(db_column='ACTIVITY_CODE', max_length=2, blank=True, null=True)  # Field name made lowercase.
#     beach_position_code = models.CharField(db_column='BEACH_POSITION_CODE', max_length=2, blank=True, null=True)  # Field name made lowercase.
#     condition_code = models.CharField(db_column='CONDITION_CODE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     nesting = models.CharField(db_column='NESTING', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     clutch_completed = models.CharField(db_column='CLUTCH_COMPLETED', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     number_of_eggs = models.SmallIntegerField(db_column='NUMBER_OF_EGGS', blank=True, null=True)  # Field name made lowercase.
#     egg_count_method = models.CharField(db_column='EGG_COUNT_METHOD', max_length=3, blank=True, null=True)  # Field name made lowercase.
#     measurements = models.CharField(db_column='MEASUREMENTS', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     action_taken = models.CharField(db_column='ACTION_TAKEN', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     comments = models.TextField(db_column='COMMENTS', blank=True, null=True)  # Field name made lowercase.
#     entered_by = models.CharField(db_column='ENTERED_BY', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     date_entered = models.DateTimeField(db_column='DATE_ENTERED', blank=True, null=True)  # Field name made lowercase.
#     original_observation_id = models.IntegerField(db_column='ORIGINAL_OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.
#     entry_batch_id = models.IntegerField(db_column='ENTRY_BATCH_ID', blank=True, null=True)  # Field name made lowercase.
#     comment_fromrecordedtagstable = models.TextField(db_column='COMMENT_FROMRECORDEDTAGSTABLE', blank=True, null=True)  # Field name made lowercase.
#     scars_left = models.BooleanField(db_column='SCARS_LEFT')  # Field name made lowercase.
#     scars_right = models.BooleanField(db_column='SCARS_RIGHT')  # Field name made lowercase.
#     other_tags = models.CharField(db_column='OTHER_TAGS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     turtledetailsincorrect = models.BooleanField(db_column='TurtleDetailsIncorrect')  # Field name made lowercase.
#     turtledetailscomment = models.CharField(db_column='TurtleDetailsComment', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     other_tags_identification_type = models.CharField(db_column='OTHER_TAGS_IDENTIFICATION_TYPE', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     entered_by_person_id = models.IntegerField(db_column='ENTERED_BY_PERSON_ID', blank=True, null=True)  # Field name made lowercase.
#     newturtle = models.BooleanField(db_column='NewTurtle')  # Field name made lowercase.
#     scars_left_scale_1 = models.BooleanField(db_column='SCARS_LEFT_SCALE_1')  # Field name made lowercase.
#     scars_left_scale_2 = models.BooleanField(db_column='SCARS_LEFT_SCALE_2')  # Field name made lowercase.
#     scars_left_scale_3 = models.BooleanField(db_column='SCARS_LEFT_SCALE_3')  # Field name made lowercase.
#     scars_right_scale_1 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_1')  # Field name made lowercase.
#     scars_right_scale_2 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_2')  # Field name made lowercase.
#     scars_right_scale_3 = models.BooleanField(db_column='SCARS_RIGHT_SCALE_3')  # Field name made lowercase.
#     cc_length_not_measured = models.BooleanField(db_column='CC_LENGTH_Not_Measured')  # Field name made lowercase.
#     cc_notch_length_not_measured = models.BooleanField(db_column='CC_NOTCH_LENGTH_Not_Measured')  # Field name made lowercase.
#     cc_width_not_measured = models.BooleanField(db_column='CC_WIDTH_Not_Measured')  # Field name made lowercase.
#     tagscarnotchecked = models.BooleanField(db_column='TagScarNotChecked')  # Field name made lowercase.
#     didnotcheckforinjury = models.BooleanField(db_column='DidNotCheckForInjury')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblObservations'


# class TblpersonsImport(models.Model):
#     person_id = models.IntegerField(db_column='PERSON_ID')  # Field name made lowercase.
#     first_name = models.CharField(db_column='FIRST_NAME', max_length=50)  # Field name made lowercase.
#     middle_name = models.CharField(db_column='MIDDLE_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     surname = models.CharField(db_column='SURNAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     specialty = models.CharField(db_column='SPECIALTY', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     address_line_1 = models.CharField(db_column='ADDRESS_LINE_1', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     address_line_2 = models.CharField(db_column='ADDRESS_LINE_2', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     town = models.CharField(db_column='TOWN', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     state = models.CharField(db_column='STATE', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     post_code = models.CharField(db_column='POST_CODE', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     country = models.CharField(db_column='COUNTRY', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     telephone = models.CharField(db_column='TELEPHONE', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     fax = models.CharField(db_column='FAX', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     mobile = models.CharField(db_column='MOBILE', max_length=20, blank=True, null=True)  # Field name made lowercase.
#     email = models.CharField(db_column='EMAIL', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     transfer = models.CharField(db_column='Transfer', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     recorder = models.BooleanField(db_column='Recorder')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblPERSONS_Import'


# class TblrecordedPitTags(models.Model):
#     recorded_pittag_id = models.IntegerField(db_column='RECORDED_pittag_id')  # Field name made lowercase.
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
#     pittag_id = models.CharField(db_column='pittag_id', max_length=50)  # Field name made lowercase.
#     pit_tag_state = models.CharField(db_column='PIT_TAG_STATE', max_length=10)  # Field name made lowercase.
#     pit_tag_position = models.CharField(db_column='PIT_TAG_POSITION', max_length=10)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     checked = models.BooleanField(db_column='Checked')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblRecorded_Pit_Tags'


# class TblrecordedTags(models.Model):
#     recorded_tag_id = models.IntegerField(db_column='RECORDED_TAG_ID')  # Field name made lowercase.
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID')  # Field name made lowercase.
#     tag_id = models.CharField(db_column='TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     other_tag_id = models.CharField(db_column='OTHER_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     side = models.CharField(db_column='SIDE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     tag_state = models.CharField(db_column='TAG_STATE', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     tag_position = models.SmallIntegerField(db_column='TAG_POSITION', blank=True, null=True)  # Field name made lowercase.
#     barnacles = models.BooleanField(db_column='BARNACLES')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblRecorded_Tags'


# class TbltransferRecordedPitTags(models.Model):
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.
#     pittag_id = models.CharField(db_column='pittag_id', max_length=50)  # Field name made lowercase.
#     pit_tag_state = models.CharField(db_column='PIT_TAG_STATE', max_length=10)  # Field name made lowercase.
#     pit_tag_position = models.CharField(db_column='PIT_TAG_POSITION', max_length=10)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     turtle_id = models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
#     checked = models.BooleanField(db_column='Checked', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblTransfer_RECORDED_PIT_TAGS'


# class TbltransferRecordedTags(models.Model):
#     observation_id = models.IntegerField(db_column='OBSERVATION_ID', blank=True, null=True)  # Field name made lowercase.
#     tag_id = models.CharField(db_column='TAG_ID', max_length=10)  # Field name made lowercase.
#     other_tag_id = models.CharField(db_column='OTHER_TAG_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     side = models.CharField(db_column='SIDE', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     tag_state = models.CharField(db_column='TAG_STATE', max_length=10, blank=True, null=True)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     turtle_id = models.IntegerField(db_column='TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
#     tag_position = models.SmallIntegerField(db_column='TAG_POSITION', blank=True, null=True)  # Field name made lowercase.
#     barnacles = models.BooleanField(db_column='BARNACLES', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblTransfer_RECORDED_TAGS'


# class Tblturtles(models.Model):
#     turtle_id = models.IntegerField(db_column='TURTLE_ID')  # Field name made lowercase.
#     species_code = models.CharField(db_column='SPECIES_CODE', max_length=2)  # Field name made lowercase.
#     identification_confidence = models.CharField(db_column='IDENTIFICATION_CONFIDENCE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     sex = models.CharField(db_column='SEX', max_length=1)  # Field name made lowercase.
#     turtle_status = models.CharField(db_column='TURTLE_STATUS', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     location_code = models.CharField(db_column='LOCATION_CODE', max_length=2, blank=True, null=True)  # Field name made lowercase.
#     cause_of_death = models.CharField(db_column='CAUSE_OF_DEATH', max_length=2, blank=True, null=True)  # Field name made lowercase.
#     comments = models.CharField(db_column='COMMENTS', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     entered_by = models.CharField(db_column='ENTERED_BY', max_length=50, blank=True, null=True)  # Field name made lowercase.
#     date_entered = models.DateTimeField(db_column='DATE_ENTERED', blank=True, null=True)  # Field name made lowercase.
#     original_turtle_id = models.IntegerField(db_column='ORIGINAL_TURTLE_ID', blank=True, null=True)  # Field name made lowercase.
#     entry_batch_id = models.IntegerField(db_column='ENTRY_BATCH_ID', blank=True, null=True)  # Field name made lowercase.
#     re_entered_population = models.CharField(db_column='RE_ENTERED_POPULATION', max_length=1, blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblTurtles'


# class TblversionBackend(models.Model):
#     version = models.IntegerField(db_column='Version', primary_key=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'tblVersion_Backend'
