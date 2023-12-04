# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


# class Sysdiagrams(models.Model):
#     name = models.TextField()
#     principal_id = models.IntegerField()
#     diagram_id = models.BigAutoField(primary_key=True)
#     version = models.IntegerField(blank=True, null=True)
#     definition = models.BinaryField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'sysdiagrams'
#         unique_together = (('principal_id', 'name'),)


# class Tbldamage(models.Model):
#     observation_id = models.IntegerField()
#     body_part = models.TextField()
#     damage_code = models.TextField()
#     damage_cause_code = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tbldamage'


# class TblimportEntryBatchId(models.Model):
#     entry_batch_id = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tblimport_entry_batch_id'


# class TblimportObservationid(models.Model):
#     obs_observation_id = models.IntegerField(blank=True, null=True)
#     admin_observation_id = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tblimport_observationid'


# class TblimportPersonid(models.Model):
#     obs_person_id = models.IntegerField(blank=True, null=True)
#     admin_person_id = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tblimport_personid'


# class TblimportTurtleid(models.Model):
#     obs_turtle_id = models.IntegerField(blank=True, null=True)
#     admin_turtle_id = models.IntegerField(blank=True, null=True)
#     newturtle = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'tblimport_turtleid'


# class Tblmeasurements(models.Model):
#     observation_id = models.IntegerField()
#     measurement_type = models.TextField()
#     measurement_value = models.FloatField()
#     comments = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tblmeasurements'


# class Tblobservations(models.Model):
#     observation_id = models.IntegerField()
#     turtle_id = models.IntegerField()
#     observation_date_old = models.DateTimeField(blank=True, null=True)
#     observation_date = models.DateTimeField()
#     observation_time = models.DateTimeField(blank=True, null=True)
#     alive = models.TextField(blank=True, null=True)
#     measurer_person_id = models.IntegerField(blank=True, null=True)
#     tagger_person_id = models.IntegerField(blank=True, null=True)
#     reporter_person_id = models.IntegerField(blank=True, null=True)
#     measurer_reporter_person_id = models.IntegerField(blank=True, null=True)
#     place_code = models.TextField(blank=True, null=True)
#     place_description = models.TextField(blank=True, null=True)
#     datum_code = models.TextField(blank=True, null=True)
#     latitude = models.FloatField(blank=True, null=True)
#     longitude = models.FloatField(blank=True, null=True)
#     latitude_degrees = models.IntegerField(blank=True, null=True)
#     latitude_minutes = models.FloatField(blank=True, null=True)
#     latitude_seconds = models.FloatField(blank=True, null=True)
#     longitude_degrees = models.IntegerField(blank=True, null=True)
#     longitude_minutes = models.FloatField(blank=True, null=True)
#     longitude_seconds = models.FloatField(blank=True, null=True)
#     zone = models.IntegerField(blank=True, null=True)
#     easting = models.FloatField(blank=True, null=True)
#     northing = models.FloatField(blank=True, null=True)
#     activity_code = models.TextField(blank=True, null=True)
#     beach_position_code = models.TextField(blank=True, null=True)
#     condition_code = models.TextField(blank=True, null=True)
#     nesting = models.TextField(blank=True, null=True)
#     clutch_completed = models.TextField(blank=True, null=True)
#     number_of_eggs = models.SmallIntegerField(blank=True, null=True)
#     egg_count_method = models.TextField(blank=True, null=True)
#     measurements = models.TextField(blank=True, null=True)
#     action_taken = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     entered_by = models.TextField(blank=True, null=True)
#     date_entered = models.DateTimeField(blank=True, null=True)
#     original_observation_id = models.IntegerField(blank=True, null=True)
#     entry_batch_id = models.IntegerField(blank=True, null=True)
#     comment_fromrecordedtagstable = models.TextField(blank=True, null=True)
#     scars_left = models.BooleanField()
#     scars_right = models.BooleanField()
#     other_tags = models.TextField(blank=True, null=True)
#     turtledetailsincorrect = models.BooleanField()
#     turtledetailscomment = models.TextField(blank=True, null=True)
#     other_tags_identification_type = models.TextField(blank=True, null=True)
#     entered_by_person_id = models.IntegerField(blank=True, null=True)
#     newturtle = models.BooleanField()
#     scars_left_scale_1 = models.BooleanField()
#     scars_left_scale_2 = models.BooleanField()
#     scars_left_scale_3 = models.BooleanField()
#     scars_right_scale_1 = models.BooleanField()
#     scars_right_scale_2 = models.BooleanField()
#     scars_right_scale_3 = models.BooleanField()
#     cc_length_not_measured = models.BooleanField()
#     cc_notch_length_not_measured = models.BooleanField()
#     cc_width_not_measured = models.BooleanField()
#     tagscarnotchecked = models.BooleanField()
#     didnotcheckforinjury = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'tblobservations'


# class TblpersonsImport(models.Model):
#     person_id = models.IntegerField()
#     first_name = models.TextField()
#     middle_name = models.TextField(blank=True, null=True)
#     surname = models.TextField(blank=True, null=True)
#     specialty = models.TextField(blank=True, null=True)
#     address_line_1 = models.TextField(blank=True, null=True)
#     address_line_2 = models.TextField(blank=True, null=True)
#     town = models.TextField(blank=True, null=True)
#     state = models.TextField(blank=True, null=True)
#     post_code = models.TextField(blank=True, null=True)
#     country = models.TextField(blank=True, null=True)
#     telephone = models.TextField(blank=True, null=True)
#     fax = models.TextField(blank=True, null=True)
#     mobile = models.TextField(blank=True, null=True)
#     email = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     transfer = models.TextField(blank=True, null=True)
#     recorder = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'tblpersons_import'


# class TblrecordedPitTags(models.Model):
#     recorded_pit_tag_id = models.IntegerField()
#     observation_id = models.IntegerField()
#     pit_tag_id = models.TextField()
#     pit_tag_state = models.TextField()
#     pit_tag_position = models.TextField()
#     comments = models.TextField(blank=True, null=True)
#     checked = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'tblrecorded_pit_tags'


# class TblrecordedTags(models.Model):
#     recorded_tag_id = models.IntegerField()
#     observation_id = models.IntegerField()
#     tag_id = models.TextField(blank=True, null=True)
#     other_tag_id = models.TextField(blank=True, null=True)
#     side = models.TextField(blank=True, null=True)
#     tag_state = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     tag_position = models.SmallIntegerField(blank=True, null=True)
#     barnacles = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'tblrecorded_tags'


# class TbltransferRecordedPitTags(models.Model):
#     observation_id = models.IntegerField(blank=True, null=True)
#     pit_tag_id = models.TextField()
#     pit_tag_state = models.TextField()
#     pit_tag_position = models.TextField()
#     comments = models.TextField(blank=True, null=True)
#     turtle_id = models.IntegerField(blank=True, null=True)
#     checked = models.BooleanField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tbltransfer_recorded_pit_tags'


# class TbltransferRecordedTags(models.Model):
#     observation_id = models.IntegerField(blank=True, null=True)
#     tag_id = models.TextField()
#     other_tag_id = models.TextField(blank=True, null=True)
#     side = models.TextField(blank=True, null=True)
#     tag_state = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     turtle_id = models.IntegerField(blank=True, null=True)
#     tag_position = models.SmallIntegerField(blank=True, null=True)
#     barnacles = models.BooleanField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tbltransfer_recorded_tags'


# class Tblturtles(models.Model):
#     turtle_id = models.IntegerField()
#     species_code = models.TextField()
#     identification_confidence = models.TextField(blank=True, null=True)
#     sex = models.TextField()
#     turtle_status = models.TextField(blank=True, null=True)
#     location_code = models.TextField(blank=True, null=True)
#     cause_of_death = models.TextField(blank=True, null=True)
#     comments = models.TextField(blank=True, null=True)
#     entered_by = models.TextField(blank=True, null=True)
#     date_entered = models.DateTimeField(blank=True, null=True)
#     original_turtle_id = models.IntegerField(blank=True, null=True)
#     entry_batch_id = models.IntegerField(blank=True, null=True)
#     re_entered_population = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'tblturtles'


# class TblversionBackend(models.Model):
#     version = models.IntegerField(primary_key=True)

#     class Meta:
#         managed = False
#         db_table = 'tblversion_backend'


class TrtActivities(models.Model):
    activity_code = models.TextField(primary_key=True)
    description = models.TextField()
    nesting = models.TextField()
    new_code = models.TextField(blank=True, null=True)
    display_observation = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_activities'
    
    def __str__(self):
        return f"{self.description}"



class TrtBeachPositions(models.Model):
    beach_position_code = models.TextField(primary_key=True)
    description = models.TextField()
    new_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_beach_positions'


class TrtBodyParts(models.Model):
    body_part = models.TextField(primary_key=True)
    description = models.TextField()
    flipper = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_body_parts'
    def __str__(self):
        return f"{self.description}"


class TrtCauseOfDeath(models.Model):
    cause_of_death = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_cause_of_death'


class TrtConditionCodes(models.Model):
    condition_code = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_condition_codes'

    def __str__(self):
        return f"{self.description}"
    

class TrtDamage(models.Model):
    observation = models.OneToOneField('TrtObservations', models.DO_NOTHING, primary_key=True)
    body_part = models.ForeignKey(TrtBodyParts, models.DO_NOTHING, db_column='body_part')
    damage_code = models.ForeignKey('TrtDamageCodes', models.DO_NOTHING, db_column='damage_code')
    damage_cause_code = models.ForeignKey('TrtDamageCauseCodes', models.DO_NOTHING, db_column='damage_cause_code', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_damage'
        unique_together = (('observation', 'body_part'),)


class TrtDamageCause(models.Model):
    observation_id = models.IntegerField()
    body_part = models.TextField()
    damage_code = models.TextField()
    damage_cause_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_damage_cause'


class TrtDamageCauseCodes(models.Model):
    damage_cause_code = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_damage_cause_codes'
    def __str__(self):
        return f"{self.description}"


class TrtDamageCodes(models.Model):
    damage_code = models.TextField(primary_key=True)
    description = models.TextField()
    flipper = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_damage_codes'
    def __str__(self):
        return f"{self.description}"


class TrtDataChanged(models.Model):
    trt_data_changed_id = models.BigAutoField(primary_key=True)
    datachanged_date = models.DateTimeField(blank=True, null=True)
    datachangedby = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_data_changed'


class TrtDataEntry(models.Model):
    data_entry_id = models.BigAutoField(primary_key=True)
    entry_batch = models.ForeignKey('TrtEntryBatches', models.DO_NOTHING)
    user_entry_id = models.IntegerField()
    turtle_id = models.IntegerField(blank=True, null=True)
    observation_id = models.IntegerField(blank=True, null=True)
    do_not_process = models.BooleanField()
    recapture_left_tag_id = models.TextField(blank=True, null=True)
    recapture_left_tag_id_2 = models.TextField(blank=True, null=True)
    recapture_right_tag_id = models.TextField(blank=True, null=True)
    recapture_right_tag_id_2 = models.TextField(blank=True, null=True)
    recapture_pit_tag_id = models.TextField(blank=True, null=True)
    other_left_tag = models.TextField(blank=True, null=True)
    other_right_tag = models.TextField(blank=True, null=True)
    new_left_tag_id = models.TextField(blank=True, null=True)
    new_left_tag_id_2 = models.TextField(blank=True, null=True)
    new_right_tag_id = models.TextField(blank=True, null=True)
    new_right_tag_id_2 = models.TextField(blank=True, null=True)
    new_pit_tag_id = models.TextField(blank=True, null=True)
    alive = models.TextField(blank=True, null=True)
    place_code = models.TextField(blank=True, null=True)
    observation_date = models.DateTimeField(blank=True, null=True)
    observation_time = models.DateTimeField(blank=True, null=True)
    nesting = models.TextField(blank=True, null=True)
    species_code = models.TextField(blank=True, null=True)
    identification_confidence = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    curved_carapace_length = models.IntegerField(blank=True, null=True)
    curved_carapace_width = models.IntegerField(blank=True, null=True)
    activity_code = models.TextField(blank=True, null=True)
    beach_position_code = models.TextField(blank=True, null=True)
    damage_carapace = models.TextField(blank=True, null=True)
    damage_lff = models.TextField(blank=True, null=True)
    damage_rff = models.TextField(blank=True, null=True)
    damage_lhf = models.TextField(blank=True, null=True)
    damage_rhf = models.TextField(blank=True, null=True)
    body_part_1 = models.TextField(blank=True, null=True)
    damage_code_1 = models.TextField(blank=True, null=True)
    body_part_2 = models.TextField(blank=True, null=True)
    damage_code_2 = models.TextField(blank=True, null=True)
    egg_count = models.IntegerField(blank=True, null=True)
    egg_count_method = models.TextField(blank=True, null=True)
    clutch_completed = models.TextField(blank=True, null=True)
    measured_by = models.TextField(blank=True, null=True)
    recorded_by = models.TextField(blank=True, null=True)
    tagged_by = models.TextField(blank=True, null=True)
    entered_by = models.TextField(blank=True, null=True)
    measured_recorded_by = models.TextField(blank=True, null=True)
    measurement_type_1 = models.TextField(blank=True, null=True)
    measurement_value_1 = models.FloatField(blank=True, null=True)
    measurement_type_2 = models.TextField(blank=True, null=True)
    measurement_value_2 = models.FloatField(blank=True, null=True)
    datum_code = models.TextField(blank=True, null=True)
    zone = models.IntegerField(blank=True, null=True)
    easting = models.FloatField(blank=True, null=True)
    northing = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude_degrees = models.IntegerField(blank=True, null=True)
    latitude_minutes = models.FloatField(blank=True, null=True)
    latitude_seconds = models.FloatField(blank=True, null=True)
    longitude_degrees = models.IntegerField(blank=True, null=True)
    longitude_minutes = models.FloatField(blank=True, null=True)
    longitude_seconds = models.FloatField(blank=True, null=True)
    identification_type = models.TextField(blank=True, null=True)
    identifier = models.TextField(blank=True, null=True)
    comment_fromrecordedtagstable = models.TextField(blank=True, null=True)
    scars_left = models.BooleanField()
    scars_right = models.BooleanField()
    other_tags = models.TextField(blank=True, null=True)
    other_tags_identification_type = models.TextField(blank=True, null=True)
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
    comments = models.TextField(blank=True, null=True)
    error_number = models.IntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    recapture_left_tag_id_3 = models.TextField(blank=True, null=True)
    recapture_right_tag_id_3 = models.TextField(blank=True, null=True)
    body_part_3 = models.TextField(blank=True, null=True)
    damage_code_3 = models.TextField(blank=True, null=True)
    tissue_type_1 = models.TextField(blank=True, null=True)
    sample_label_1 = models.TextField(blank=True, null=True)
    tissue_type_2 = models.TextField(blank=True, null=True)
    sample_label_2 = models.TextField(blank=True, null=True)
    turtle_comments = models.TextField(blank=True, null=True)
    recapture_pit_tag_id_2 = models.TextField(blank=True, null=True)
    new_pit_tag_id_2 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_data_entry'
        unique_together = (('entry_batch', 'user_entry_id'),)


class TrtDataEntryExceptions(models.Model):
    entry_batch_id = models.IntegerField(primary_key=True)
    data_entry_id = models.IntegerField()
    turtle_id = models.IntegerField(blank=True, null=True)
    observation_id = models.IntegerField(blank=True, null=True)
    recapture_left_tag_id = models.TextField(blank=True, null=True)
    recapture_right_tag_id = models.TextField(blank=True, null=True)
    recapture_left_tag_id_2 = models.TextField(blank=True, null=True)
    recapture_right_tag_id_2 = models.TextField(blank=True, null=True)
    other_left_tag = models.TextField(blank=True, null=True)
    other_right_tag = models.TextField(blank=True, null=True)
    new_left_tag_id = models.TextField(blank=True, null=True)
    new_right_tag_id = models.TextField(blank=True, null=True)
    alive = models.TextField(blank=True, null=True)
    place_code = models.TextField(blank=True, null=True)
    observation_date = models.DateTimeField(blank=True, null=True)
    observation_time = models.DateTimeField(blank=True, null=True)
    nesting = models.TextField(blank=True, null=True)
    species_code = models.TextField(blank=True, null=True)
    identification_confidence = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    curved_carapace_length = models.IntegerField(blank=True, null=True)
    curved_carapace_width = models.IntegerField(blank=True, null=True)
    activity_code = models.TextField(blank=True, null=True)
    beach_position_code = models.TextField(blank=True, null=True)
    damage_carapace = models.TextField(blank=True, null=True)
    damage_lff = models.TextField(blank=True, null=True)
    damage_rff = models.TextField(blank=True, null=True)
    damage_lhf = models.TextField(blank=True, null=True)
    damage_rhf = models.TextField(blank=True, null=True)
    clutch_completed = models.TextField(blank=True, null=True)
    egg_count = models.IntegerField(blank=True, null=True)
    egg_count_method = models.TextField(blank=True, null=True)
    measured_by = models.TextField(blank=True, null=True)
    recorded_by = models.TextField(blank=True, null=True)
    tagged_by = models.TextField(blank=True, null=True)
    measurement_type_1 = models.TextField(blank=True, null=True)
    measurement_value_1 = models.FloatField(blank=True, null=True)
    measurement_type_2 = models.TextField(blank=True, null=True)
    measurement_value_2 = models.FloatField(blank=True, null=True)
    datum_code = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude_degrees = models.IntegerField(blank=True, null=True)
    latitude_minutes = models.FloatField(blank=True, null=True)
    latitude_seconds = models.FloatField(blank=True, null=True)
    longitude_degrees = models.IntegerField(blank=True, null=True)
    longitude_minutes = models.FloatField(blank=True, null=True)
    longitude_seconds = models.FloatField(blank=True, null=True)
    zone = models.IntegerField(blank=True, null=True)
    easting = models.FloatField(blank=True, null=True)
    northing = models.FloatField(blank=True, null=True)
    identification_type = models.TextField(blank=True, null=True)
    identifier = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_data_entry_exceptions'
        unique_together = (('entry_batch_id', 'data_entry_id'),)


class TrtDataEntryPersons(models.Model):
    data_entry_person_id = models.BigAutoField(primary_key=True)
    entry_batch = models.ForeignKey('TrtEntryBatches', models.DO_NOTHING)
    person_name = models.TextField()
    person_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_data_entry_persons'
        unique_together = (('entry_batch', 'person_name'),)


class TrtDatumCodes(models.Model):
    datum_code = models.TextField(primary_key=True)
    datum_description = models.TextField(blank=True, null=True)
    semi_major_axis = models.FloatField(blank=True, null=True)
    inverse_flattening = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_datum_codes'


class TrtDefault(models.Model):
    id = models.TextField(primary_key=True)
    dataentry_exportpath = models.TextField()
    dataentry_sourcedatabase = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_default'


class TrtDocumentTypes(models.Model):
    document_type = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_document_types'


class TrtDocuments(models.Model):
    document_id = models.BigAutoField(primary_key=True)
    document_type = models.TextField()
    filename = models.TextField(blank=True, null=True)
    turtle_id = models.IntegerField(blank=True, null=True)
    person_id = models.IntegerField(blank=True, null=True)
    species_code = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_documents'


class TrtEggCountMethods(models.Model):
    egg_count_method = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_egg_count_methods'


class TrtEntryBatches(models.Model):
    entry_batch_id = models.BigAutoField(primary_key=True)
    entry_date = models.DateTimeField(blank=True, null=True)
    entered_person_id = models.IntegerField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    pr_date_convention = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_entry_batches'
    def __str__(self):
        return f"{self.entry_batch_id}"



class TrtIdentification(models.Model):
    turtle = models.OneToOneField('TrtTurtles', models.DO_NOTHING, primary_key=True)
    identification_type = models.ForeignKey('TrtIdentificationTypes', models.DO_NOTHING, db_column='identification_type')
    identifier = models.TextField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_identification'
        unique_together = (('turtle', 'identification_type', 'identifier'),)


class TrtIdentificationTypes(models.Model):
    identification_type = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_identification_types'


class TrtLocations(models.Model):
    location_code = models.TextField(primary_key=True)
    location_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_locations'

    def __str__(self):
        return f"{self.location_name}"


class TrtMeasurementTypes(models.Model):
    measurement_type = models.TextField(primary_key=True)
    description = models.TextField()
    measurement_units = models.TextField(blank=True, null=True)
    minimum_value = models.FloatField(blank=True, null=True)
    maximum_value = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_measurement_types'

    def __str__(self):
            return f"{self.description}"

class TrtMeasurements(models.Model):
    id = models.AutoField(primary_key=True)
    observation = models.ForeignKey('TrtObservations', on_delete=models.CASCADE)
    measurement_type = models.ForeignKey(TrtMeasurementTypes, on_delete=models.CASCADE, db_column='measurement_type')
    measurement_value = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'trt_measurements'
        unique_together = (('observation', 'measurement_type'),)


class TrtNesting(models.Model):
    place_code = models.TextField(primary_key=True)
    species_code = models.TextField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_nesting'
        unique_together = (('place_code', 'species_code'),)


class TrtNestingSeason(models.Model):
    nesting_seasonid = models.BigAutoField(primary_key=True)
    nesting_season = models.TextField()
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'trt_nesting_season'


class TrtObservations(models.Model):
    observation_id = models.BigAutoField(primary_key=True)
    turtle = models.ForeignKey('TrtTurtles', models.DO_NOTHING)
    observation_date = models.DateTimeField()
    observation_time = models.DateTimeField(blank=True, null=True)
    observation_date_old = models.DateTimeField(blank=True, null=True)
    alive = models.TextField(blank=True, null=True)
    measurer_person = models.ForeignKey('TrtPersons', models.DO_NOTHING, blank=True, null=True,related_name='measurer_person')
    measurer_reporter_person = models.ForeignKey('TrtPersons', models.DO_NOTHING, blank=True, null=True,related_name='measurer_reporter_person')
    tagger_person = models.ForeignKey('TrtPersons', models.DO_NOTHING, blank=True, null=True,related_name='tagger_person')
    reporter_person = models.ForeignKey('TrtPersons', models.DO_NOTHING, blank=True, null=True)
    place_code = models.ForeignKey('TrtPlaces', models.DO_NOTHING, db_column='place_code', blank=True, null=True)
    place_description = models.TextField(blank=True, null=True)
    datum_code = models.ForeignKey(TrtDatumCodes, models.DO_NOTHING, db_column='datum_code', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude_degrees = models.IntegerField(blank=True, null=True)
    latitude_minutes = models.FloatField(blank=True, null=True)
    latitude_seconds = models.FloatField(blank=True, null=True)
    longitude_degrees = models.IntegerField(blank=True, null=True)
    longitude_minutes = models.FloatField(blank=True, null=True)
    longitude_seconds = models.FloatField(blank=True, null=True)
    zone = models.IntegerField(blank=True, null=True)
    easting = models.FloatField(blank=True, null=True)
    northing = models.FloatField(blank=True, null=True)
    activity_code = models.ForeignKey(TrtActivities, models.DO_NOTHING, db_column='activity_code', blank=True, null=True)
    beach_position_code = models.ForeignKey(TrtBeachPositions, models.DO_NOTHING, db_column='beach_position_code', blank=True, null=True)
    condition_code = models.ForeignKey(TrtConditionCodes, models.DO_NOTHING, db_column='condition_code', blank=True, null=True)
    nesting = models.TextField(blank=True, null=True)
    clutch_completed = models.TextField(blank=True, null=True)
    number_of_eggs = models.SmallIntegerField(blank=True, null=True)
    egg_count_method = models.ForeignKey(TrtEggCountMethods, models.DO_NOTHING, db_column='egg_count_method', blank=True, null=True)
    measurements = models.TextField()
    action_taken = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    entered_by = models.TextField(blank=True, null=True)
    date_entered = models.DateTimeField(blank=True, null=True)
    original_observation_id = models.IntegerField(blank=True, null=True)
    entry_batch = models.ForeignKey(TrtEntryBatches, models.DO_NOTHING, blank=True, null=True)
    comment_fromrecordedtagstable = models.TextField(blank=True, null=True)
    scars_left = models.BooleanField()
    scars_right = models.BooleanField()
    other_tags = models.TextField(blank=True, null=True)
    other_tags_identification_type = models.ForeignKey(TrtIdentificationTypes, models.DO_NOTHING, db_column='other_tags_identification_type', blank=True, null=True)
    transferid = models.IntegerField(blank=True, null=True)
    mund = models.BooleanField()
    entered_by_person = models.ForeignKey('TrtPersons', models.DO_NOTHING, blank=True, null=True,related_name='entered_by_person')
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
    date_convention = models.TextField()
    observation_status = models.TextField(blank=True, null=True)
    corrected_date = models.DateTimeField(blank=True, null=True)
    

    class Meta:
        managed = False
        db_table = 'trt_observations'
        unique_together = (('observation_id', 'turtle'),)
        verbose_name = "Observation"

    def __str__(self):
        return f"{self.observation_id}"


class TrtPersons(models.Model):
    person_id = models.BigAutoField(primary_key=True)
    first_name = models.TextField()
    middle_name = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    specialty = models.TextField(blank=True, null=True)
    address_line_1 = models.TextField(blank=True, null=True)
    address_line_2 = models.TextField(blank=True, null=True)
    town = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    post_code = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    telephone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    mobile = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    transfer = models.TextField(blank=True, null=True)
    recorder = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_persons'
    def __str__(self):
        return f"{self.first_name} {self.surname}"


class TrtPitTagStates(models.Model):
    pit_tag_state = models.TextField(primary_key=True)
    description = models.TextField()
    pit_tag_status = models.ForeignKey('TrtPitTagStatus', models.DO_NOTHING, db_column='pit_tag_status')
    existing_tag_list = models.BooleanField()
    new_tag_list = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_pit_tag_states'


class TrtPitTagStatus(models.Model):
    pit_tag_status = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_pit_tag_status'
    
    def __str__(self):
        return f"{self.description}"


class TrtPitTags(models.Model):
    pit_tag_id = models.TextField(primary_key=True)
    issue_location = models.TextField(blank=True, null=True)
    custodian_person_id = models.IntegerField(blank=True, null=True)
    turtle = models.ForeignKey('TrtTurtles', models.DO_NOTHING, blank=True, null=True)
    pit_tag_status = models.TextField(blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)
    return_condition = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    field_person_id = models.IntegerField(blank=True, null=True)
    tag_order_id = models.IntegerField(blank=True, null=True)
    batch_number = models.TextField(blank=True, null=True)
    box_number = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_pit_tags'
        unique_together = (('pit_tag_id', 'turtle'),)
        verbose_name = "Pit tag"


class TrtPlaces(models.Model):
    place_code = models.TextField(primary_key=True)
    place_name = models.TextField(blank=True, null=True)
    location_code = models.TextField()
    rookery = models.TextField(blank=True, null=True)
    beach_approach = models.TextField(blank=True, null=True)
    aspect = models.TextField(blank=True, null=True)
    datum_code = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_places'
    
    def __str__(self):
        return f"{self.place_name}"


class TrtRecordedIdentification(models.Model):
    recorded_identification_id = models.BigAutoField(primary_key=True)
    observation_id = models.IntegerField()
    turtle = models.ForeignKey(TrtIdentification, models.DO_NOTHING)
    identification_type = models.TextField()
    identifier = models.TextField()
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_recorded_identification'


class TrtRecordedPitTags(models.Model):
    recorded_pit_tag_id = models.BigAutoField(primary_key=True)
    observation_id = models.IntegerField()
    pit_tag_id = models.TextField()
    pit_tag_state = models.ForeignKey(TrtPitTagStates, models.DO_NOTHING, db_column='pit_tag_state')
    pit_tag_position = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    turtle_id = models.IntegerField()
    checked = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_recorded_pit_tags'


class TrtRecordedTags(models.Model):
    recorded_tag_id = models.BigAutoField(primary_key=True)
    observation_id = models.IntegerField()
    tag_id = models.TextField()
    other_tag_id = models.TextField(blank=True, null=True)
    side = models.TextField(blank=True, null=True)
    tag_state = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    tag_position = models.SmallIntegerField(blank=True, null=True)
    barnacles = models.BooleanField()
    turtle_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'trt_recorded_tags'


class TrtSamples(models.Model):
    sample_id = models.BigAutoField(primary_key=True)
    turtle = models.ForeignKey('TrtTurtles', models.DO_NOTHING)
    sample_date = models.DateTimeField(blank=True, null=True)
    tissue_type = models.ForeignKey('TrtTissueTypes', models.DO_NOTHING, db_column='tissue_type')
    arsenic = models.FloatField(blank=True, null=True)
    selenium = models.FloatField(blank=True, null=True)
    zinc = models.FloatField(blank=True, null=True)
    cadmium = models.FloatField(blank=True, null=True)
    copper = models.FloatField(blank=True, null=True)
    lead = models.FloatField(blank=True, null=True)
    mercury = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    observation_id = models.IntegerField(blank=True, null=True)
    sample_label = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_samples'


class TrtSighting(models.Model):
    sightingid = models.BigAutoField(primary_key=True)
    observation_time = models.DateTimeField(blank=True, null=True)
    observation_date = models.DateTimeField(blank=True, null=True)
    alive = models.TextField(blank=True, null=True)
    species_code = models.TextField(blank=True, null=True)
    sex = models.TextField(blank=True, null=True)
    location_code = models.TextField(blank=True, null=True)
    turtle_status = models.TextField(blank=True, null=True)
    place_code = models.TextField(blank=True, null=True)
    activity_code = models.TextField(blank=True, null=True)
    beach_position_code = models.TextField(blank=True, null=True)
    datum_code = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    entered_by_person_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_sighting'


class TrtSpecies(models.Model):
    species_code = models.TextField(primary_key=True)
    scientific_name = models.TextField(blank=True, null=True)
    common_name = models.TextField(blank=True, null=True)
    old_species_code = models.TextField(blank=True, null=True)
    hide_dataentry = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_species'

    def __str__(self):
        return f"{self.common_name}"


class TrtTagOrders(models.Model):
    tag_order_id = models.BigAutoField(primary_key=True)
    order_date = models.DateTimeField(blank=True, null=True)
    order_number = models.TextField()
    tag_prefix = models.TextField(blank=True, null=True)
    start_tag_number = models.IntegerField(blank=True, null=True)
    end_tag_number = models.IntegerField(blank=True, null=True)
    total_tags = models.SmallIntegerField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)
    paid_by = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_tag_orders'


class TrtTagStates(models.Model):
    tag_state = models.TextField(primary_key=True)
    description = models.TextField()
    tag_status = models.TextField(blank=True, null=True)
    existing_tag_list = models.BooleanField()
    new_tag_list = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_tag_states'
    def __str__(self):
        return f"{self.description}"


class TrtTagStatus(models.Model):
    tag_status = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_tag_status'
    def __str__(self):
        return f"{self.description}"


class TrtTags(models.Model):
    tag_id = models.TextField(primary_key=True)
    tag_order_id = models.IntegerField(blank=True, null=True)
    issue_location = models.TextField(blank=True, null=True)
    custodian_person_id = models.IntegerField(blank=True, null=True)
    turtle = models.ForeignKey('TrtTurtles', models.DO_NOTHING, blank=True, null=True)
    side = models.TextField(blank=True, null=True)
    tag_status = models.ForeignKey(TrtTagStatus, models.DO_NOTHING, db_column='tag_status', blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)
    return_condition = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    field_person_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_tags'
        unique_together = (('tag_id', 'turtle'),)
        verbose_name = "Flipper tag"


class TrtTissueTypes(models.Model):
    tissue_type = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_tissue_types'


class TrtTurtleStatus(models.Model):
    turtle_status = models.TextField(primary_key=True)
    description = models.TextField()
    new_tag_list = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'trt_turtle_status'

    def __str__(self):
            return f"{self.description}"


class TrtTurtles(models.Model):
    turtle_id = models.IntegerField(primary_key=True)
    species_code = models.ForeignKey(TrtSpecies, models.DO_NOTHING, db_column='species_code')
    identification_confidence = models.TextField(blank=True, null=True)
    sex = models.TextField()
    turtle_status = models.ForeignKey(TrtTurtleStatus, models.DO_NOTHING, db_column='turtle_status', blank=True, null=True)
    location_code = models.ForeignKey(TrtLocations, models.DO_NOTHING, db_column='location_code', blank=True, null=True)
    cause_of_death = models.ForeignKey(TrtCauseOfDeath, models.DO_NOTHING, db_column='cause_of_death', blank=True, null=True)
    re_entered_population = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    entered_by = models.TextField(blank=True, null=True)
    date_entered = models.DateTimeField(blank=True, null=True)
    original_turtle_id = models.IntegerField(blank=True, null=True)
    entry_batch_id = models.IntegerField(blank=True, null=True)
    tag = models.TextField(blank=True, null=True)
    mund_id = models.TextField(blank=True, null=True)
    turtle_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trt_turtles'
        verbose_name = "Turtle"
    
    def __str__(self):
        return f"{self.turtle_id}"

class TrtYesNo(models.Model):
    code = models.TextField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'trt_yes_no'
