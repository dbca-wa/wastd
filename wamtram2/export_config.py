FIELD_HEADER_MAP = {
    # Legacy naming
    "entry_batch": "ENTRY_BATCH_ID",
    "egg_count": "NUMBER_OF_EGGS",

    # Person IDs
    "measured_by_id": "MEASURER_PERSON_ID",
    "measured_recorded_by_id": "MEASURER_REPORTER_PERSON_ID",
    "recorded_by_id": "REPORTER_PERSON_ID",
    "tagged_by_id": "TAGGER_PERSON_ID",
    "entered_by_id": "ENTERED_BY_PERSON_ID",

    # Existing exports use this naming
    "tagscarnotchecked": "TagScarNotChecked",
    "didnotcheckforinjury": "DidNotCheckForInjury",

    # Pit tags
    "recapture_pittag_id": "RECAPTURE_PIT_TAG_ID",
    "recapture_pittag_id_2": "RECAPTURE_PIT_TAG_ID_2",
    "recapture_pittag_id_3": "RECAPTURE_PIT_TAG_ID_3",
    "recapture_pittag_id_4": "RECAPTURE_PIT_TAG_ID_4",

    "new_pittag_id": "NEW_PIT_TAG_ID",
    "new_pittag_id_2": "NEW_PIT_TAG_ID_2",
    "new_pittag_id_3": "NEW_PIT_TAG_ID_3",
    "new_pittag_id_4": "NEW_PIT_TAG_ID_4",
}

EXTRA_HEADERS = {
    "species_code": [
        "COMMON_NAME",
    ],

    "place_code": [
        "PLACE_NAME",
        "LOCATION_CODE",
        "OBSERVED_LOCATION_CODE",
        "OBSERVED_LOCATION_NAME",
    ],

    "activity_code": [
        "ACTIVITY_DESCRIPTION",
    ],

    "beach_position_code": [
        "BEACH_POSITION_DESCRIPTION",
    ],
    "measurement_type_1": [
        "MEASUREMENT_TYPE_1_DESCRIPTION",
        "MEASUREMENT_TYPE_1_UNITS",
    ],
    "measurement_type_2": [
        "MEASUREMENT_TYPE_2_DESCRIPTION",
        "MEASUREMENT_TYPE_2_UNITS",
    ],
    "measurement_type_3": [
        "MEASUREMENT_TYPE_3_DESCRIPTION",
        "MEASUREMENT_TYPE_3_UNITS",
    ],
    "measurement_type_4": [
        "MEASUREMENT_TYPE_4_DESCRIPTION",
        "MEASUREMENT_TYPE_4_UNITS",
    ],
    "measurement_type_5": [
        "MEASUREMENT_TYPE_5_DESCRIPTION",
        "MEASUREMENT_TYPE_5_UNITS",
    ],
    "measurement_type_6": [
        "MEASUREMENT_TYPE_6_DESCRIPTION",
        "MEASUREMENT_TYPE_6_UNITS",
    ],

    "body_part_1": ["BODY_PART_1_DESCRIPTION"],
    "body_part_2": ["BODY_PART_2_DESCRIPTION"],
    "body_part_3": ["BODY_PART_3_DESCRIPTION"],
    "body_part_4": ["BODY_PART_4_DESCRIPTION"],
    "body_part_5": ["BODY_PART_5_DESCRIPTION"],
    "body_part_6": ["BODY_PART_6_DESCRIPTION"],

    "damage_code_1": ["DAMAGE_CODE_1_DESCRIPTION"],
    "damage_code_2": ["DAMAGE_CODE_2_DESCRIPTION"],
    "damage_code_3": ["DAMAGE_CODE_3_DESCRIPTION"],
    "damage_code_4": ["DAMAGE_CODE_4_DESCRIPTION"],
    "damage_code_5": ["DAMAGE_CODE_5_DESCRIPTION"],
    "damage_code_6": ["DAMAGE_CODE_6_DESCRIPTION"],

    "tissue_type_1": ["TISSUE_TYPE_1_DESCRIPTION"],
    "tissue_type_2": ["TISSUE_TYPE_2_DESCRIPTION"],
    "tissue_type_3": ["TISSUE_TYPE_3_DESCRIPTION"],
    "tissue_type_4": ["TISSUE_TYPE_4_DESCRIPTION"],

    "new_left_tag_state": ["NEW_LEFT_TAG_STATE_DESCRIPTION"],
    "new_left_tag_state_2": ["NEW_LEFT_TAG_STATE_2_DESCRIPTION"],
    "new_right_tag_state": ["NEW_RIGHT_TAG_STATE_DESCRIPTION"],
    "new_right_tag_state_2": ["NEW_RIGHT_TAG_STATE_2_DESCRIPTION"],

    "recapture_left_tag_state": ["RECAPTURE_LEFT_TAG_STATE_DESCRIPTION"],
    "recapture_left_tag_state_2": ["RECAPTURE_LEFT_TAG_STATE_2_DESCRIPTION"],
    "recapture_right_tag_state": ["RECAPTURE_RIGHT_TAG_STATE_DESCRIPTION"],
    "recapture_right_tag_state_2": ["RECAPTURE_RIGHT_TAG_STATE_2_DESCRIPTION"],

    "damage_carapace": ["DAMAGE_CARAPACE_DESCRIPTION"],
    "damage_lff": ["DAMAGE_LFF_DESCRIPTION"],
    "damage_rff": ["DAMAGE_RFF_DESCRIPTION"],
    "damage_lhf": ["DAMAGE_LHF_DESCRIPTION"],
    "damage_rhf": ["DAMAGE_RHF_DESCRIPTION"],

    "measured_by_id": ["MEASURER_PERSON_NAME"],
    "measured_recorded_by_id": ["MEASURER_REPORTER_PERSON_NAME"],
    "tagged_by_id": ["TAGGER_PERSON_NAME"],
    "recorded_by_id": ["REPORTER_PERSON_NAME"],
    "entered_by_id": ["DATA_ENTERER_NAME"],

    "sex": [
        "TURTLE_STATUS",
    ],

    "egg_count_method": [
        "MEASUREMENTS",
    ],


    "other_tags": [
        "OTHER_IDENTIFICATION",
        "TAG_1",
        "TAG_2",
        "TAG_3",
        "TAG_4",
        "ALL_FLIPPER_TAGS",
        "PIT_TAGS",
        "ALL_PIT_TAGS",
    ],

}

PERSON_FIELDS = {
    "measured_by_id",
    "measured_recorded_by_id",
    "tagged_by_id",
    "recorded_by_id",
    "entered_by_id",
}

BODY_PART_FIELDS = {
    "body_part_1",
    "body_part_2",
    "body_part_3",
    "body_part_4",
    "body_part_5",
    "body_part_6",
}

DAMAGE_CODE_FIELDS = {
    "damage_code_1",
    "damage_code_2",
    "damage_code_3",
    "damage_code_4",
    "damage_code_5",
    "damage_code_6",
}

TISSUE_FIELDS = {
    "tissue_type_1",
    "tissue_type_2",
    "tissue_type_3",
    "tissue_type_4",
}

TAG_STATE_FIELDS = {
    "new_left_tag_state",
    "new_left_tag_state_2",
    "new_right_tag_state",
    "new_right_tag_state_2",
    "recapture_left_tag_state",
    "recapture_left_tag_state_2",
    "recapture_right_tag_state",
    "recapture_right_tag_state_2",
}

DAMAGE_FIELDS = {
    "damage_carapace",
    "damage_lff",
    "damage_rff",
    "damage_lhf",
    "damage_rhf",
}


PROCESSED_EXPORT_HEADERS = [
    "OBSERVATION_ID",
    "TURTLE_ID",
    "OBSERVATION_DATE",
    "OBSERVATION_TIME",
    "OBSERVATION_DATE_OLD",
    "ALIVE",
    "ENTRY_ID",
    "DATA_ENTRY_ID",
    "USER_ENTRY_ID",
    "DATE_ENTERED",
    "ORIGINAL_OBSERVATION_ID",
    "ENTRY_BATCH_ID",
    "DATA_ENTERER_ID",
    "DATA_ENTERER_NAME",
    "MEASURER_PERSON_ID",
    "MEASURER_PERSON_NAME",
    "MEASURER_REPORTER_PERSON_ID",
    "MEASURER_REPORTER_PERSON_NAME",
    "TAGGER_PERSON_ID",
    "TAGGER_PERSON_NAME",
    "REPORTER_PERSON_ID",
    "REPORTER_PERSON_NAME",
    "ENTERED_BY_PERSON_ID",
    "ENTERED_BY_PERSON_NAME",
    "PLACE_CODE",
    "PLACE_DESCRIPTION",
    "DATUM_CODE",
    "LATITUDE",
    "LONGITUDE",
    "LATITUDE_DEGREES",
    "LATITUDE_MINUTES",
    "LATITUDE_SECONDS",
    "LONGITUDE_DEGREES",
    "LONGITUDE_MINUTES",
    "LONGITUDE_SECONDS",
    "ZONE",
    "EASTING",
    "NORTHING",
    "ACTIVITY_CODE",
    "ACTIVITY_DESCRIPTION",
    "BEACH_POSITION_CODE",
    "BEACH_POSITION_DESCRIPTION",
    "CONDITION_CODE",
    "CONDITION_DESCRIPTION",
    "NESTING",
    "CLUTCH_COMPLETED",
    "NUMBER_OF_EGGS",
    "EGG_COUNT_METHOD",
    "EGG_COUNT_METHOD_DESCRIPTION",
    "MEASUREMENTS",
    "ALL_MEASUREMENTS",
    "ACTION_TAKEN",
    "COMMENTS",
    "DATA_ENTRY_COMMENTS",
    "FLIPPER_TAG_COMMENTS",
    "PIT_TAG_COMMENTS",
    "ENTERED_BY",
    "COMMENT_FROMRECORDEDTAGSTABLE",
    "SCARS_LEFT",
    "SCARS_RIGHT",
    "OTHER_TAGS",
    "OTHER_TAGS_IDENTIFICATION_TYPE",
    "TransferID",
    "SCARS_LEFT_SCALE_1",
    "SCARS_LEFT_SCALE_2",
    "SCARS_LEFT_SCALE_3",
    "SCARS_RIGHT_SCALE_1",
    "SCARS_RIGHT_SCALE_2",
    "SCARS_RIGHT_SCALE_3",
    "CC_LENGTH_Not_Measured",
    "CC_NOTCH_LENGTH_Not_Measured",
    "CC_WIDTH_Not_Measured",
    "TagScarNotChecked",
    "DidNotCheckForInjury",
    "OBSERVATION_STATUS",
    "NEW_TURTLE",
    "DUD_FLIPPER_TAG",
    "DUD_FLIPPER_TAG_2",
    "DUD_PIT_TAG",
    "DUD_PIT_TAG_2",
    "SPECIES_CODE",
    "COMMON_NAME",
    "IDENTIFICATION_CONFIDENCE",
    "SEX",
    "TURTLE_STATUS",
    "IDENTIFICATIONS",
    "TAG_1",
    "TAG_2",
    "TAG_3",
    "TAG_4",
    "ALL_FLIPPER_TAGS",
    "FLIPPER_TAG_DETAILS",
    "PIT_TAGS",
    "PIT_TAG_DETAILS",
    "LOCATION_CODE",
    "OBSERVED_LOCATION_CODE",
    "OBSERVED_LOCATION_NAME",
    "PLACE_NAME",
    "DAMAGE",
    "SAMPLES",
]


UNRESOLVED_PROCESSED_EXPORT_COLUMNS = {
    "ENTRY_ID": "No matching model field was found in TrtDataEntry or TrtObservations.",
    "DATA_ENTERER_ID": "The processed observation table has ENTERED_BY_PERSON_ID; no separate DATA_ENTERER_ID field was found.",
    "DATA_ENTERER_NAME": "The processed observation table has ENTERED_BY/ENTERED_BY_PERSON_ID; no separate DATA_ENTERER_NAME field was found.",
    "FLIPPER_TAG_COMMENTS": "No dedicated processed flipper-tag comment column was found; tag comments are included in FLIPPER_TAG_DETAILS.",
    "PIT_TAG_COMMENTS": "No dedicated processed PIT-tag comment column was found; PIT comments are included in PIT_TAG_DETAILS.",
}
