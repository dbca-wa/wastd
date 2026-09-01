from collections import defaultdict
from datetime import date, datetime, time
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError

from .models import (
    TrtDamage,
    TrtDataEntry,
    TrtEntryBatchOrganisation,
    TrtMeasurements,
    TrtObservations,
    TrtRecordedIdentification,
    TrtRecordedPitTags,
    TrtRecordedTags,
)

from .export_config import (
    BODY_PART_FIELDS,
    DAMAGE_CODE_FIELDS,
    TISSUE_FIELDS,
    TAG_STATE_FIELDS,
    DAMAGE_FIELDS,
    PERSON_FIELDS,
    PROCESSED_EXPORT_HEADERS,
)
from .export_config import (
    FIELD_HEADER_MAP,
    EXTRA_HEADERS,
)

EXTRA_EXPORT_FIELDS = ("organisations",)
SQLSERVER_IN_CHUNK_SIZE = 900

def build_export_headers(
    model_meta,
    entry_type,
):
    headers = []

    for field in model_meta.fields:
        header = FIELD_HEADER_MAP.get(
            field.name,
            field.name.upper(),
        )
        # ENTRY_ID uses the same value as DATA_ENTRY_ID.
        if entry_type == "field" and field.name == "data_entry_id":
            headers.append("ENTRY_ID")

        headers.append(header)

        headers.extend(
            EXTRA_HEADERS.get(
                field.name,
                [],
            )
        )

    headers.append("ORGANISATIONS")

    if entry_type == "field":
        headers.append("OBSERVATION_STATUS")

    return headers
def get_entry_organisation_lookup(entries):
    batch_ids = {entry.entry_batch_id for entry in entries if entry.entry_batch_id}
    organisations_by_batch = defaultdict(list)

    if not batch_ids:
        return organisations_by_batch

    for batch_id, organisation in _safe_query_by_chunks(
        batch_ids,
        lambda chunk: TrtEntryBatchOrganisation.objects.filter(
            trtentrybatch_id__in=chunk
        ).values_list("trtentrybatch_id", "organisation"),
    ):
        organisations_by_batch[batch_id].append(organisation)

    return organisations_by_batch

def get_export_field_value(
    entry,
    field,
    entry_type,
):
    name = field.name

    if (
        name == "observation_id"
        and entry_type == "field"
    ):
        return entry.observation_id_id or ""

    elif (
        name == "turtle"
        and entry_type == "processed"
    ):
        return entry.turtle_id or ""

    if field.is_relation and field.many_to_one:
        return getattr(
            entry,
            f"{name}_id",
            "",
        )

    value = getattr(entry, name)

    if (
        name == "observation_date"
        and isinstance(value, datetime)
        and timezone.is_aware(value)
    ):
        return timezone.localtime(value).date()

    if (
        name == "observation_time"
        and isinstance(value, datetime)
        and timezone.is_aware(value)
    ):
        return timezone.localtime(value).time()

    return value




def format_export_value(value):
    if isinstance(value, datetime):

        # Excel time-only
        if value.date() == date(1899, 12, 30):
            return value.strftime("%I:%M:%S %p").lstrip("0")

        # Normal datetime with time
        if value.time() == time(0, 0):
            return value.strftime("%m/%d/%Y")

        # other datetime
        return value.strftime("%m/%d/%Y %I:%M:%S %p")

    if isinstance(value, date):
        return value.strftime("%m/%d/%Y")

    if isinstance(value, bool):
        return "True" if value else "False"

    if value is None:
        return ""

    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
  
    return str(value)
    
def get_extra_field_values(
    entry,
    field_name,
    beach_position_dict,
    summary_dict=None,
):
    if field_name == "species_code":
        return [
            getattr(entry.species_code, "common_name", "")
        ]

    elif field_name == "place_code":
        place = entry.place_code
        location = getattr(place, "location_code", None)
        
        return [
            getattr(place, "place_name", ""), # PLACE_DESCRIPTION
            getattr(place, "place_name", ""), # PLACE_NAME
            getattr(location, "location_code", ""),
            getattr(location, "location_code", ""),
            getattr(location, "location_name", ""),
        ]
    elif field_name == "entered_by_id":
        person = getattr(entry, "entered_by_id", None)

        return [
            getattr(entry, "entered_by_id_id", "") or "",
            (
                f"{person.first_name} {person.surname}".strip()
                if person
                else ""
            ),
        ]

    elif field_name == "activity_code":
        return [
            getattr(entry.activity_code, "description", "")
        ]

    elif field_name == "beach_position_code":
        return [
            beach_position_dict.get(
                entry.beach_position_code,
                "",
            )
        ]
    elif field_name == "sex":
        summary = summary_dict.get(
            entry.observation_id_id
            if summary_dict
                else None
        )

        return [
            summary.turtle_status
            if summary
            else ""
        ]

    elif field_name == "egg_count_method":
        summary = (
            summary_dict.get(entry.observation_id_id)
            if summary_dict
            else None
        )

        if summary:
            return [
                (
                    f"CCL={summary.ccl or ''}; "
                    f"CCL_NOTCH={summary.ccl_notch or ''}; "
                    f"CCW={summary.ccw or ''}"
                )
            ]

        return [""]

    elif field_name == "other_tags":

        flipper_tags = []

        for tag_field in [
            "new_left_tag_id",
            "new_left_tag_id_2",
            "new_right_tag_id",
            "new_right_tag_id_2",
            "recapture_left_tag_id",
            "recapture_left_tag_id_2",
            "recapture_left_tag_id_3",
            "recapture_right_tag_id",
            "recapture_right_tag_id_2",
            "recapture_right_tag_id_3",
        ]:
            value = getattr(
                entry,
                f"{tag_field}_id",
                None,
            )

            if value:
                flipper_tags.append(str(value))

        pit_tags = []

        for pit_field in [
            "new_pittag_id",
            "new_pittag_id_2",
            "new_pittag_id_3",
            "new_pittag_id_4",
            "recapture_pittag_id",
            "recapture_pittag_id_2",
            "recapture_pittag_id_3",
            "recapture_pittag_id_4",
        ]:
            value = getattr(
                entry,
                f"{pit_field}_id",
                None,
            )

            if value:
                pit_tags.append(str(value))

        return [
            getattr(entry, "other_identification", ""),

            # TAG_1
            getattr(entry, "new_left_tag_id_id", "") or "",

            # TAG_2
            getattr(entry, "new_right_tag_id_id", "") or "",

            # TAG_3
            getattr(entry, "recapture_left_tag_id_id", "") or "",

            # TAG_4
            getattr(entry, "recapture_right_tag_id_id", "") or "",

            # ALL_FLIPPER_TAGS
            "; ".join(flipper_tags),

            # PIT_TAGS
            pit_tags[0] if pit_tags else "",

            # ALL_PIT_TAGS
            "; ".join(pit_tags),
        ]

    return []

def get_lookup_values(
    entry,
    field_name,
    measurement_type_dict,
    body_part_dict,
    damage_code_dict,
    tissue_type_dict,
    tag_state_dict,
):
    if field_name.startswith("measurement_type_"):
        mt = measurement_type_dict.get(
            getattr(entry, f"{field_name}_id")
        )

        return [
            getattr(mt, "description", ""),
            getattr(mt, "measurement_units", ""),
        ]

    elif field_name in BODY_PART_FIELDS:
        value = getattr(entry, f"{field_name}_id")

        return [
            getattr(
                body_part_dict.get(value),
                "description",
                "",
            )
        ]

    elif field_name in DAMAGE_CODE_FIELDS:
        value = getattr(entry, f"{field_name}_id")

        return [
            getattr(
                damage_code_dict.get(value),
                "description",
                "",
            )
        ]


    elif field_name in TISSUE_FIELDS:
        return [
            getattr(
                tissue_type_dict.get(
                    getattr(entry, field_name)
                ),
                "description",
                "",
            )
        ]

    elif field_name in TAG_STATE_FIELDS:
        value = getattr(entry, f"{field_name}_id")

        return [
            getattr(
                tag_state_dict.get(value),
                "description",
                "",
            )
        ]

    elif field_name in DAMAGE_FIELDS:
        value = getattr(entry, f"{field_name}_id")

        return [
            getattr(
                damage_code_dict.get(value),
                "description",
                "",
            )
        ]

    elif field_name in PERSON_FIELDS:
        person = getattr(entry, field_name)

        return [
            str(person)
            if person
            else ""
        ]

    return []

def get_observation_status(entry):
    if (
        entry.observation_id_id is not None
        and getattr(entry, "observation_id", None)
    ):
        return (
            entry.observation_id.observation_status
            or ""
        )

    return ""

def get_field_export_row(
    entry,
    organisations_by_batch,
    beach_position_dict,
    summary_dict,
    measurement_type_dict,
    body_part_dict,
    damage_code_dict,
    tissue_type_dict,
    tag_state_dict,
):
    row = []

    for field in TrtDataEntry._meta.fields:
        row.append(format_export_value(get_export_field_value(entry, field, "field")))

        for value in get_extra_field_values(
            entry,
            field.name,
            beach_position_dict,
            summary_dict,
        ):
            row.append(format_export_value(value))

        for value in get_lookup_values(
            entry,
            field.name,
            measurement_type_dict,
            body_part_dict,
            damage_code_dict,
            tissue_type_dict,
            tag_state_dict,
        ):
            row.append(format_export_value(value))

    row.append(", ".join(organisations_by_batch.get(entry.entry_batch_id, [])))
    row.append(format_export_value(get_observation_status(entry)))

    return row
    
def _chunks(values, size=SQLSERVER_IN_CHUNK_SIZE):
    values = list(values)
    for index in range(0, len(values), size):
        yield values[index : index + size]

def _safe_query_by_chunks(values, build_queryset):
    results = []
    for chunk in _chunks(values):
        results.extend(_safe_queryset(build_queryset(chunk)))
    return results

def get_processed_export_headers():
    return PROCESSED_EXPORT_HEADERS

def _observation_id_set(entries):
    observation_ids = set()
    for entry in entries:
        value = _attr(entry, "observation_id")
        if hasattr(value, "observation_id"):
            value = value.observation_id
        if value not in (None, ""):
            observation_ids.add(value)
    return observation_ids

def build_processed_export_context(entries):
    observation_ids = _observation_id_set(entries)
    turtle_ids = _raw_id_set(entries, "turtle")

    context = {
        "observations": {},
        "data_entries": {},
        "first_observations": {},
        "recorded_tags": defaultdict(list),
        "recorded_pit_tags": defaultdict(list),
        "measurements": defaultdict(list),
        "damages": defaultdict(list),
        "identifications": defaultdict(list),
    }

    if not observation_ids:
        return context

    context["observations"] = {
        observation.observation_id: observation
        for observation in _safe_query_by_chunks(
            observation_ids,
            lambda chunk: TrtObservations.objects.filter(observation_id__in=chunk)
            .select_related(
                "activity_code",
                "alive",
                "beach_position_code",
                "clutch_completed",
                "condition_code",
                "datum_code",
                "egg_count_method",
                "entered_by_person",
                "measurer_person",
                "measurer_reporter_person",
                "nesting",
                "place_code",
                "place_code__location_code",
                "reporter_person",
                "tagger_person",
                "turtle",
                "turtle__location_code",
                "turtle__species_code",
                "turtle__turtle_status",
            ),
        )
    }

    for turtle_id, observation_date, observation_id in _safe_query_by_chunks(
        turtle_ids,
        lambda chunk: TrtObservations.objects.filter(turtle_id__in=chunk)
        .order_by("turtle_id", "observation_date", "observation_id")
        .values_list("turtle_id", "observation_date", "observation_id"),
    ):
        context["first_observations"].setdefault(
            turtle_id,
            (observation_date, observation_id),
        )

    context["data_entries"] = {
        data_entry.observation_id_id: data_entry
        for data_entry in _safe_query_by_chunks(
            observation_ids,
            lambda chunk: TrtDataEntry.objects.filter(observation_id__in=chunk)
            .select_related(
                "species_code",
                "place_code",
                "activity_code",
                "nesting",
                "alive",
                "measured_by_id",
                "recorded_by_id",
                "tagged_by_id",
                "entered_by_id",
                "measured_recorded_by_id",
                "egg_count_method",
                "clutch_completed",
            ),
        )
        if data_entry.observation_id_id
    }


    for tag in _safe_query_by_chunks(
        observation_ids,
        lambda chunk: TrtRecordedTags.objects.filter(observation_id_id__in=chunk)
        .select_related("tag_id", "tag_state")
        .order_by(
            "observation_id_id",
            "side",
            "tag_position",
            "recorded_tag_id",
        ),
    ):
        context["recorded_tags"][tag.observation_id_id].append(tag)

    for pit_tag in _safe_query_by_chunks(
        observation_ids,
        lambda chunk: TrtRecordedPitTags.objects.filter(observation_id_id__in=chunk)
        .select_related("pittag_id", "pit_tag_state")
        .order_by(
            "observation_id_id",
            "pit_tag_position",
            "recorded_pittag_id",
        ),
    ):
        context["recorded_pit_tags"][pit_tag.observation_id_id].append(
            pit_tag
        )

    for measurement in _safe_query_by_chunks(
        observation_ids,
        lambda chunk: TrtMeasurements.objects.filter(observation_id__in=chunk)
        .select_related("measurement_type")
        .order_by(
            "observation_id",
            "measurement_type_id",
        ),
    ):
        context["measurements"][
            measurement.observation_id
        ].append(measurement)

    for damage in _safe_query_by_chunks(
        observation_ids,
        lambda chunk: TrtDamage.objects.filter(observation_id__in=chunk)
        .select_related(
            "body_part",
            "damage_code",
            "damage_cause_code",
        )
        .order_by(
            "observation_id",
            "body_part_id",
        ),
    ):
        context["damages"][
            damage.observation_id
        ].append(damage)

    for identification in _safe_query_by_chunks(
        observation_ids,
        lambda chunk: TrtRecordedIdentification.objects.filter(
            observation_id__in=chunk,
        )
        .select_related("identification_type")
        .order_by("observation_id", "recorded_identification_id"),
    ):
        context["identifications"][
            identification.observation_id
        ].append(identification)

    return context

def get_processed_export_row(entry, context):

    observation = context["observations"].get(
        entry.observation_id,
        entry,
    )

    data_entry = context["data_entries"].get(
        observation.observation_id
    )

    observation_id = observation.observation_id

    turtle = _safe_related(
        observation,
        "turtle",
    )

    place = _safe_related(
        observation,
        "place_code",
    )

    species = _safe_related(
        turtle,
        "species_code",
    )

    location = (
        _safe_related(turtle, "location_code")
        or _safe_related(place, "location_code")
    )

    recorded_tags = context["recorded_tags"].get(
        observation_id,
        [],
    )

    recorded_pit_tags = context["recorded_pit_tags"].get(
        observation_id,
        [],
    )

    measurements = context["measurements"].get(
        observation_id,
        [],
    )

    damages = context["damages"].get(
        observation_id,
        [],
    )

    identifications = context["identifications"].get(
        observation_id,
        [],
    )

    flipper_tag_ids = [_tag_value(tag) for tag in recorded_tags]
    pit_tag_ids = [_pit_tag_value(tag) for tag in recorded_pit_tags]
    tag_details = [_format_recorded_tag(tag) for tag in recorded_tags]
    pit_tag_details = [_format_recorded_pit_tag(tag) for tag in recorded_pit_tags]

    new_left_tags = []
    new_right_tags = []
    existing_left_tags = []
    existing_right_tags = []

    for tag in recorded_tags:
        tag_value = _tag_value(tag)
        tag_state = _safe_related(tag, "tag_state")
        side = _attr(tag, "side")

        if not tag_value or not tag_state:
            continue

        # Legacy Observation exports treat "#" as an existing tag,
        # despite NEW_TAG_LIST being set in TRT_TAG_STATES.
        if _raw_fk(tag, "tag_state") == "#":
            if side == "L":
                existing_left_tags.append(tag_value)
            elif side == "R":
                existing_right_tags.append(tag_value)
            continue

        if tag_state.existing_tag_list:
            if side == "L":
                existing_left_tags.append(tag_value)
            elif side == "R":
                existing_right_tags.append(tag_value)
        elif tag_state.new_tag_list:
            if side == "L":
                new_left_tags.append(tag_value)
            elif side == "R":
                new_right_tags.append(tag_value)
                        
    obs_dt = (
        timezone.localtime(_attr(observation, "observation_date"))
        if _attr(observation, "observation_date")
        else None
    )

    #bs_time = _attr(observation, "observation_time")

    
    de = data_entry
    values = {
    "OBSERVATION_ID": observation.observation_id,
    "TURTLE_ID": _raw_fk(observation, "turtle"),
    "OBSERVATION_DATE": (
        obs_dt.date()
        if obs_dt
        else ""
    ),

    "OBSERVATION_TIME": (
        obs_dt.time()
        if obs_dt
        else ""
    ),

    "DATE_ENTERED": (
        _attr(observation, "date_entered").date()
        if _attr(observation, "date_entered")
        else ""
    ),
    "OBSERVATION_DATE_OLD": _attr(observation, "observation_date_old"),
    "ALIVE": _raw_fk(observation, "alive"),

    
    "ENTRY_ID": (
        de.data_entry_id if de else ""
    ),

    "DATA_ENTRY_ID": (
        de.data_entry_id if de else ""
    ),

    "USER_ENTRY_ID": (
        de.user_entry_id if de else ""
    ),

    "ORIGINAL_OBSERVATION_ID": _attr(observation, "original_observation_id"),

    "ENTRY_BATCH_ID": _raw_fk(
        observation,
        "entry_batch",
    ),

    "DATA_ENTERER_ID": "",
    "DATA_ENTERER_NAME": "",

    "MEASURER_PERSON_ID": _raw_fk(
        observation,
        "measurer_person",
    ),

    "MEASURER_PERSON_NAME": _person_name(
        _safe_related(
            observation,
            "measurer_person",
        )
    ),

    "MEASURER_REPORTER_PERSON_ID": _raw_fk(
        observation,
        "measurer_reporter_person",
    ),

    "MEASURER_REPORTER_PERSON_NAME": _person_name(
        _safe_related(
            observation,
            "measurer_reporter_person",
        )
    ),

    "TAGGER_PERSON_ID": _raw_fk(
        observation,
        "tagger_person",
    ),

    "TAGGER_PERSON_NAME": _person_name(
        _safe_related(
            observation,
            "tagger_person",
        )
    ),

    "REPORTER_PERSON_ID": _raw_fk(
        observation,
        "reporter_person",
    ),

    "REPORTER_PERSON_NAME": _person_name(
        _safe_related(
            observation,
            "reporter_person",
        )
    ),

    "ENTERED_BY_PERSON_ID": _raw_fk(
        observation,
        "entered_by_person",
    ),

    "ENTERED_BY_PERSON_NAME": _person_name(
        _safe_related(
            observation,
            "entered_by_person",
        )
    ),

    "PLACE_CODE": _raw_fk(
        observation,
        "place_code",
    ),

    "PLACE_DESCRIPTION": _first(
        _attr(observation, "place_description"),
        _attr(place, "place_name"),
    ),

    "DATUM_CODE": _raw_fk(
        observation,
        "datum_code",
    ),

    "LATITUDE": _attr(
        observation,
        "latitude",
    ),

    "LONGITUDE": _attr(
        observation,
        "longitude",
    ),

    "LATITUDE_DEGREES": _attr(
        observation,
        "latitude_degrees",
    ),

    "LATITUDE_MINUTES": _attr(
        observation,
        "latitude_minutes",
    ),

    "LATITUDE_SECONDS": _attr(
        observation,
        "latitude_seconds",
    ),

    "LONGITUDE_DEGREES": _attr(
        observation,
        "longitude_degrees",
    ),

    "LONGITUDE_MINUTES": _attr(
        observation,
        "longitude_minutes",
    ),

    "LONGITUDE_SECONDS": _attr(
        observation,
        "longitude_seconds",
    ),

    "ZONE": _attr(
        observation,
        "zone",
    ),

    "EASTING": _attr(
        observation,
        "easting",
    ),

    "NORTHING": _attr(
        observation,
        "northing",
    ),

    "ACTIVITY_CODE": _raw_fk(
        observation,
        "activity_code",
    ),

    "ACTIVITY_DESCRIPTION": _description(
        _safe_related(
            observation,
            "activity_code",
        )
    ),

    "BEACH_POSITION_CODE": _raw_fk(
        observation,
        "beach_position_code",
    ),

    "BEACH_POSITION_DESCRIPTION": _description(
        _safe_related(
            observation,
            "beach_position_code",
        )
    ),

    "CONDITION_CODE": _raw_fk(
        observation,
        "condition_code",
    ),

    "CONDITION_DESCRIPTION": _description(
        _safe_related(
            observation,
            "condition_code",
        )
    ),

    "NESTING": _raw_fk(
        observation,
        "nesting",
    ),

    "CLUTCH_COMPLETED": _raw_fk(
        observation,
        "clutch_completed",
    ),

    "NUMBER_OF_EGGS": _attr(
        observation,
        "number_of_eggs",
    ),

    "EGG_COUNT_METHOD": _raw_fk(
        observation,
        "egg_count_method",
    ),

    "EGG_COUNT_METHOD_DESCRIPTION": _description(
        _safe_related(
            observation,
            "egg_count_method",
        )
    ),

    "MEASUREMENTS": _attr(
        observation,
        "measurements",
    ),

    "ALL_MEASUREMENTS": _join(
        _format_measurement(m)
        for m in measurements
    ),

    "ACTION_TAKEN": _attr(
        observation,
        "action_taken",
    ),

    "COMMENTS": _attr(
        observation,
        "comments",
    ),

    "DATA_ENTRY_COMMENTS": (
        de.comments if de else ""
    ),

    "FLIPPER_TAG_COMMENTS": _join(
        tag.comments
        for tag in recorded_tags
    ),

    "PIT_TAG_COMMENTS": _join(
        tag.comments
        for tag in recorded_pit_tags
    ),

    "ENTERED_BY": _attr(
    observation,
    "entered_by",
    ),

    "COMMENT_FROMRECORDEDTAGSTABLE": _attr(
        observation,
        "comment_fromrecordedtagstable",
    ),

    "SCARS_LEFT": _attr(
        observation,
        "scars_left",
    ),

    "SCARS_RIGHT": _attr(
        observation,
        "scars_right",
    ),

    "OTHER_TAGS": _attr(
        observation,
        "other_tags",
    ),

    "OTHER_TAGS_IDENTIFICATION_TYPE": _raw_fk(
        observation,
        "other_tags_identification_type",
    ),

    "TransferID": _attr(
        observation,
        "transferid",
    ),

    "SCARS_LEFT_SCALE_1": _attr(observation, "scars_left_scale_1"),
    "SCARS_LEFT_SCALE_2": _attr(observation, "scars_left_scale_2"),
    "SCARS_LEFT_SCALE_3": _attr(observation, "scars_left_scale_3"),
    "SCARS_RIGHT_SCALE_1": _attr(observation, "scars_right_scale_1"),
    "SCARS_RIGHT_SCALE_2": _attr(observation, "scars_right_scale_2"),
    "SCARS_RIGHT_SCALE_3": _attr(observation, "scars_right_scale_3"),

    "CC_LENGTH_Not_Measured": _attr(observation, "cc_length_not_measured"),
    "CC_NOTCH_LENGTH_Not_Measured": _attr(observation, "cc_notch_length_not_measured"),
    "CC_WIDTH_Not_Measured": _attr(observation, "cc_width_not_measured"),

    "TagScarNotChecked": _attr(observation, "tagscarnotchecked"),
    "DidNotCheckForInjury": _attr(observation, "didnotcheckforinjury"),

    "OBSERVATION_STATUS": _attr(
        observation,
        "observation_status",
    ),
    "NEW_TURTLE": "Y" if is_new_turtle_observation(observation, context) else "N",

    "DUD_FLIPPER_TAG": _attr(observation, "dud_flipper_tag"),
    "DUD_FLIPPER_TAG_2": _attr(observation, "dud_flipper_tag_2"),
    "DUD_PIT_TAG": _attr(observation, "dud_pit_tag"),
    "DUD_PIT_TAG_2": _attr(observation, "dud_pit_tag_2"),

    "SPECIES_CODE": _raw_fk(
        turtle,
        "species_code",
    ),

    "COMMON_NAME": _attr(
        species,
        "common_name",
    ),

    "IDENTIFICATION_CONFIDENCE": _attr(
        turtle,
        "identification_confidence",
    ),

    "SEX": _attr(
        turtle,
        "sex",
    ),

    "TURTLE_STATUS": _first(
        _raw_fk(turtle, "turtle_status"),
        _description(
            _safe_related(
                turtle,
                "turtle_status",
            )
        ),
    ),

    "IDENTIFICATIONS": _join(
        _format_identification(i)
        for i in identifications
    ),

    # "TAG_1": _list_item(flipper_tag_ids, 0),
    # "TAG_2": _list_item(flipper_tag_ids, 1),
    # "TAG_3": _list_item(flipper_tag_ids, 2),
    # "TAG_4": _list_item(flipper_tag_ids, 3),

    # Match the legacy Observation mapping: new tags in TAG_1/TAG_2
    # and existing tags in TAG_3/TAG_4, grouped by side.
    "TAG_1": ", ".join(new_left_tags),
    "TAG_2": ", ".join(new_right_tags),
    "TAG_3": ", ".join(existing_left_tags),
    "TAG_4": ", ".join(existing_right_tags),

    "ALL_FLIPPER_TAGS": _join(flipper_tag_ids),
    "FLIPPER_TAG_DETAILS": _join(tag_details),

    "PIT_TAGS": _join(pit_tag_ids),
    "PIT_TAG_DETAILS": _join(pit_tag_details),

    "LOCATION_CODE": _raw_fk(location, "location_code") or _attr(location, "location_code"),
    "OBSERVED_LOCATION_CODE": _raw_fk(location, "location_code") or _attr(location, "location_code"),
    "OBSERVED_LOCATION_NAME": _attr(location, "location_name"),

    "PLACE_NAME": _attr(place, "place_name"),

    "DAMAGE": _join(
        _format_damage(d)
        for d in damages
    ),

    "SAMPLES": (
        _entry_samples(de)
        if de
        else ""
    ),
}
    
    return [format_export_value(values.get(header)) for header in PROCESSED_EXPORT_HEADERS]


def _safe_queryset(queryset):
    return list(queryset)

def is_new_turtle_observation(observation, context):
    turtle_id = _raw_fk(observation, "turtle")
    observation_status = _attr(observation, "observation_status")

    if observation_status not in ("Initial Sighting", "Initial Nesting"):
        return False

    first_observation = context["first_observations"].get(turtle_id)
    if not first_observation:
        return False

    return first_observation == (
        _attr(observation, "observation_date"),
        _attr(observation, "observation_id"),
    )

def _raw_id_set(entries, field_name):
    return {
        value
        for value in (_raw_fk(entry, field_name) for entry in entries)
        if value not in (None, "")
    }


def _attr(obj, name):
    if obj is None:
        return None
    return getattr(obj, name, None)


def _raw_fk(obj, field_name):
    if obj is None:
        return None
    raw_name = f"{field_name}_id"
    if hasattr(obj, raw_name):
        return getattr(obj, raw_name)
    return getattr(obj, field_name, None)


def _safe_related(obj, field_name):
    if obj is None:
        return None
    try:
        return getattr(obj, field_name)
    except (AttributeError, DatabaseError, ObjectDoesNotExist):
        return None


def _first(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return ""


def _description(obj):
    return _attr(obj, "description")


def _person_name(person):
    if not person:
        return ""
    return " ".join(
        part for part in [person.first_name, person.middle_name, person.surname] if part
    )


def _join(values):
    cleaned = [str(value) for value in values if value not in (None, "")]
    return "; ".join(cleaned)


def _list_item(values, index):
    return values[index] if len(values) > index else ""


def _tag_value(recorded_tag):
    return _first(_raw_fk(recorded_tag, "tag_id"), recorded_tag.other_tag_id)


def _pit_tag_value(recorded_pit_tag):
    return _raw_fk(recorded_pit_tag, "pittag_id")


def _format_recorded_tag(recorded_tag):
    parts = [_tag_value(recorded_tag)]
    detail_parts = []
    side = recorded_tag.side or ""
    position = recorded_tag.tag_position
    if side or position:
        detail_parts.append(f"{side}{position or ''}")
    tag_state = _raw_fk(recorded_tag, "tag_state")
    if tag_state:
        detail_parts.append(f"state={tag_state}")
    detail_parts.append(f"barnacles={recorded_tag.barnacles}")
    if recorded_tag.comments:
        detail_parts.append(f"comments={recorded_tag.comments}")
    return f"{parts[0]} ({', '.join(detail_parts)})" if detail_parts else parts[0]


def _format_recorded_pit_tag(recorded_pit_tag):
    pit_tag = _pit_tag_value(recorded_pit_tag)
    detail_parts = []
    if recorded_pit_tag.pit_tag_position:
        detail_parts.append(f"position={recorded_pit_tag.pit_tag_position}")
    pit_tag_state = _raw_fk(recorded_pit_tag, "pit_tag_state")
    if pit_tag_state:
        detail_parts.append(f"state={pit_tag_state}")
    if recorded_pit_tag.comments:
        detail_parts.append(f"comments={recorded_pit_tag.comments}")
    return f"{pit_tag} ({', '.join(detail_parts)})" if detail_parts else pit_tag


def _format_measurement(measurement):
    measurement_type = _safe_related(measurement, "measurement_type")
    label = _first(_raw_fk(measurement, "measurement_type"), _description(measurement_type))
    units = _attr(measurement_type, "measurement_units")
    value = measurement.measurement_value
    return f"{label}={value}{units or ''}"


def _entry_measurements(entry):
    measurements = []
    for index in range(1, 7):
        measurement_type = _safe_related(entry, f"measurement_type_{index}")
        value = getattr(entry, f"measurement_value_{index}", None)
        if measurement_type or value not in (None, ""):
            label = _first(_raw_fk(entry, f"measurement_type_{index}"), _description(measurement_type))
            units = _attr(measurement_type, "measurement_units")
            measurements.append(f"{label}={value}{units or ''}")
    return _join(measurements)


def _format_damage(damage):
    body_part = _safe_related(damage, "body_part")
    damage_code = _safe_related(damage, "damage_code")
    cause = _safe_related(damage, "damage_cause_code")
    parts = [
        _first(_description(body_part), _raw_fk(damage, "body_part")),
        _first(_description(damage_code), _raw_fk(damage, "damage_code")),
    ]
    if cause:
        parts.append(_first(_description(cause), _raw_fk(damage, "damage_cause_code")))
    if damage.comments:
        parts.append(damage.comments)
    return " / ".join(part for part in parts if part)


def _entry_damage(entry):
    damages = []
    for index in range(1, 7):
        body_part = _safe_related(entry, f"body_part_{index}")
        damage_code = _safe_related(entry, f"damage_code_{index}")
        if body_part or damage_code:
            damages.append(
                " / ".join(
                    part
                    for part in [
                        _first(_description(body_part), _raw_fk(entry, f"body_part_{index}")),
                        _first(_description(damage_code), _raw_fk(entry, f"damage_code_{index}")),
                    ]
                    if part
                )
            )
    return _join(damages)


def _entry_samples(entry):
    samples = []
    for index in range(1, 5):
        tissue_type = _safe_related(entry, f"tissue_type_{index}")
        sample_label = getattr(entry, f"sample_label_{index}", None)
        if tissue_type or sample_label:
            samples.append(
                " / ".join(
                    part
                    for part in [
                        _first(_description(tissue_type), _raw_fk(entry, f"tissue_type_{index}")),
                        sample_label,
                    ]
                    if part
                )
            )
    return _join(samples)


def _format_identification(identification):
    identification_type = _safe_related(identification, "identification_type")
    return " / ".join(
        part
        for part in [
            _first(_description(identification_type), _raw_fk(identification, "identification_type")),
            identification.identifier,
            identification.comments,
        ]
        if part
    )

