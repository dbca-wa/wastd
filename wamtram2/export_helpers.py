from .export_config import (
    BODY_PART_FIELDS,
    DAMAGE_CODE_FIELDS,
    TISSUE_FIELDS,
    TAG_STATE_FIELDS,
    DAMAGE_FIELDS,
    PERSON_FIELDS,
)

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
            getattr(place, "place_name", ""),
            getattr(location, "location_code", ""),
            getattr(location, "location_code", ""),
            getattr(location, "location_name", ""),
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

            flipper_tags[0]
            if len(flipper_tags) > 0
            else "",

            flipper_tags[1]
            if len(flipper_tags) > 1
            else "",

            flipper_tags[2]
            if len(flipper_tags) > 2
            else "",

            flipper_tags[3]
            if len(flipper_tags) > 3
            else "",

            "; ".join(flipper_tags),

            pit_tags[0]
            if pit_tags
            else "",

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
            getattr(entry, field_name)
        )

        return [
            getattr(mt, "description", ""),
            getattr(mt, "measurement_units", ""),
        ]

    elif field_name in BODY_PART_FIELDS:
        return [
            getattr(
                body_part_dict.get(
                    getattr(entry, field_name)
                ),
                "description",
                "",
            )
        ]

    elif field_name in DAMAGE_CODE_FIELDS:
        return [
            getattr(
                damage_code_dict.get(
                    getattr(entry, field_name)
                ),
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
        return [
            getattr(
                tag_state_dict.get(
                    getattr(entry, field_name)
                ),
                "description",
                "",
            )
        ]

    elif field_name in DAMAGE_FIELDS:
        return [
            getattr(
                damage_code_dict.get(
                    getattr(entry, field_name)
                ),
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