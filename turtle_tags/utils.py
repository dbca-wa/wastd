from django.utils import timezone
import logging

from wamtram.models import (
    TrtPersons,
    TrtTurtles,
    TrtTagOrders,
    TrtTags,
    TrtPitTags,
    TrtObservations,
    TrtRecordedTags,
    TrtRecordedPitTags,
    TrtMeasurements,
    TrtDamage,
    TrtSamples,
)
from users.models import User
from observations.models import (
    AnimalEncounter,
    TagObservation,
    TurtleMorphometricObservation,
    TurtleDamageObservation,
    TissueSampleObservation,
)
from .models import (
    Turtle,
    TagPurchaseOrder,
    TurtleTag,
)


LOGGER = logging.getLogger("turtles")
TRT_SPECIES_MAP = {
    "FB": "natator-depressus",
    "GN": "chelonia-mydas",
    "HK": "eretmochelys-imbricata",
    "LB": "dermochelys-coriacea",
    "LO": "caretta-caretta",
    "OR": "lepidochelys-olivacea",
}
ACTIVITY_MAP = {
    "&": "captivity",
    "A": "approaching",
    "B": "approaching",
    "C": "approaching",
    "D": "approaching",
    "E": "digging-body-pit",
    "F": "excavating-egg-chamber",
    "G": "laying-eggs",
    "H": "filling-in-egg-chamber",
    "I": "returning-to-water",
    "K": "basking",
    "L": "arriving",
    "M": "general-breeding-activity",
    "N": "general-breeding-activity",
    "O": "non-breeding",
    "P": "nesting",
    "Q": "other",
    "R": "released",
    "S": "stranding-rescued",
    "V": "caught-dead",  # Dead
    "W": "captured",
    "X": "beach-washed",  # Dead
    "Y": "caught-released",
    "Z": "hunted",  # Dead
}


def import_wamtram(reload=False):
    """Utility function to import/convert data from wamtram (SQL Server) to turtle_data (local).
    The function is idempotent, and may be run multiple times safely without creating duplicate data.

    If `reload` is False, some existing records will be skipped (those having the PK brought across).
    """
    admin = User.objects.get(pk=1)

    LOGGER.info("Importing persons")
    for p in TrtPersons.objects.all():
        name = p.get_name()
        if not User.objects.filter(name__iexact=name.lower()).exists():
            User.objects.create(
                username=p.email if p.email else "_".join([p.first_name, p.surname if p.surname else ""]),
                first_name=p.first_name,
                last_name=p.surname if p.surname else "",
                email=p.email if p.email else "",
                name=name,
                phone=p.mobile if p.mobile else p.telephone,
                role=" ".join([p.specialty if p.specialty else "", p.comments if p.comments else ""]).strip(),
            )
        elif User.objects.filter(name__iexact=name.lower(), is_active=True).count() > 1:
            LOGGER.info(f"POSSIBLE DUPLICATE USER: {p}")
    LOGGER.info(f"User object count: {User.objects.count()}")

    LOGGER.info("Importing tag orders")
    for o in TrtTagOrders.objects.all():
        if TagPurchaseOrder.objects.filter(source="wamtram", source_id=o.tag_order_id).exists():
            if reload:
                po = TagPurchaseOrder.objects.get(source="wamtram", source_id=o.tag_order_id)
                po.order_number = o.order_number
                po.order_date = o.order_date.date() if o.order_date else None
                po.tag_prefix = o.tag_prefix
                po.total = o.total_tags
                po.date_received = o.date_received.date() if o.date_received else None
                po.paid_by = o.paid_by
                po.comments = o.comments
                po.save()
            else:
                continue
        else:
            TagPurchaseOrder.objects.get_or_create(
                source="wamtram",
                source_id=o.tag_order_id,
                order_number=o.order_number,
                order_date=o.order_date.date() if o.order_date else None,
                tag_prefix=o.tag_prefix,
                total=o.total_tags,
                date_received=o.date_received.date() if o.date_received else None,
                paid_by=o.paid_by,
                comments=o.comments,
            )
    LOGGER.info(f"TagPurchaseOrder object count: {TagPurchaseOrder.objects.count()}")

    LOGGER.info("Importing turtles")
    turtle_count = 0
    bobp = User.objects.get(username="bobp")
    turtle_ids = TrtTurtles.objects.values_list("turtle_id", flat=True)

    for id in turtle_ids:
        # Fast-path skip existing records, no reload.
        if Turtle.objects.filter(source="wamtram", source_id=id).exists() and not reload:
            continue
        else:
            wamtram_turtle = TrtTurtles.objects.get(turtle_id=id)

            if wamtram_turtle.species_code_id in ["?", "0"]:
                species = Turtle.TURTLE_SPECIES_DEFAULT
            else:
                species = TRT_SPECIES_MAP[wamtram_turtle.species_code_id]

            if wamtram_turtle.sex == "I":
                sex = "intersex"
            elif wamtram_turtle.sex == "F":
                sex = "female"
            elif wamtram_turtle.sex == "M":
                sex = "male"
            else:
                sex = "unknown"

            if wamtram_turtle.entered_by == "bobp":
                entered_by = bobp
            else:
                entered_by = admin

            if Turtle.objects.filter(source="wamtram", source_id=id).exists():
                if reload:
                    turtle = Turtle.objects.get(pk=wamtram_turtle.turtle_id)
                    turtle.created = wamtram_turtle.date_entered if wamtram_turtle.date_entered else timezone.now()
                    turtle.entered_by = entered_by
                    turtle.source = "wamtram"
                    turtle.source_id = id
                    turtle.species = species
                    turtle.sex = sex
                    turtle.name = wamtram_turtle.turtle_name
                    turtle.comments = wamtram_turtle.comments
                    turtle.save()
                else:
                    continue
            else:
                turtle = Turtle.objects.get_or_create(
                    pk=wamtram_turtle.turtle_id,
                    created=wamtram_turtle.date_entered if wamtram_turtle.date_entered else timezone.now(),
                    entered_by=entered_by,
                    source="wamtram",
                    source_id=id,
                    species=species,
                    sex=sex,
                    name=wamtram_turtle.turtle_name,
                    comments=wamtram_turtle.comments,
                )[0]

            turtle_count += 1
            if turtle_count % 1000 == 0:
                LOGGER.info(f"{turtle_count} imported")
    LOGGER.info(f"Turtle object count: {Turtle.objects.count()}")

    LOGGER.info("Importing flipper tags")
    tag_count = 0
    # Instantiate a list of tuples: [(<Tag serial minus spaces>, <Tag serial>), ...]
    tag_serials = TrtTags.objects.values_list("tag_id", flat=True)
    tag_serials = [(t.replace(" ", "").strip(), t) for t in tag_serials]

    for serials in tag_serials:
        # Fast-path skip existing records, no reload.
        if TurtleTag.objects.filter(serial=serials[0], tag_type="flipper-tag").exists() and not reload:
            continue
        else:
            wamtram_tag = TrtTags.objects.get(tag_id=serials[1])

            if wamtram_tag.custodian_person_id and TrtPersons.objects.filter(person_id=wamtram_tag.custodian_person_id).exists():
                wamtram_person = TrtPersons.objects.get(person_id=wamtram_tag.custodian_person_id)
                custodian = User.objects.get(name__iexact=wamtram_person.get_name(), is_active=True)
            else:
                custodian = None

            if wamtram_tag.field_person_id and TrtPersons.objects.filter(person_id=wamtram_tag.field_person_id).exists():
                wamtram_person = TrtPersons.objects.get(person_id=wamtram_tag.field_person_id)
                field_person = User.objects.get(name__iexact=wamtram_person.get_name(), is_active=True)
            else:
                field_person = None

            if Turtle.objects.filter(source="wamtram", source_id=wamtram_tag.turtle_id).exists():
                turtle = Turtle.objects.get(source="wamtram", source_id=wamtram_tag.turtle_id)
            else:
                turtle = None

            if wamtram_tag.tag_order_id and TagPurchaseOrder.objects.filter(source_id=wamtram_tag.tag_order_id).exists():
                order = TagPurchaseOrder.objects.get(source_id=wamtram_tag.tag_order_id)
            else:
                order = None

            if wamtram_tag.side == "L":
                side = "left"
            elif wamtram_tag.side == "R":
                side = "right"
            else:
                side = None

            serial = serials[0]

            if TurtleTag.objects.filter(serial=serial, tag_type="flipper-tag", source="wamtram", source_id=serial).exists():
                if reload:
                    turtle = Turtle.objects.get(source="wamtram", source_id=wamtram_tag.turtle_id)
                    tag = TurtleTag.objects.get(
                        serial=serial, tag_type="flipper-tag", source="wamtram", source_id=serial)
                    tag.turtle = turtle
                    tag.order = order
                    tag.custodian = custodian
                    tag.field_handler = field_person
                    tag.side = side
                    tag.return_date = wamtram_tag.return_date.date() if wamtram_tag.return_date else None
                    tag.return_condition = wamtram_tag.return_condition
                    tag.comments = wamtram_tag.comments
                    tag.save()
                else:
                    continue
            else:
                TurtleTag.objects.get_or_create(
                    serial=serial,
                    tag_type="flipper-tag",
                    source="wamtram",
                    source_id=serial,
                    turtle=turtle,
                    order=order,
                    custodian=custodian,
                    field_handler=field_person,
                    side=wamtram_tag.side,
                    return_date=wamtram_tag.return_date.date() if wamtram_tag.return_date else None,
                    return_condition=wamtram_tag.return_condition,
                    comments=wamtram_tag.comments,
                )
            tag_count += 1
            if tag_count % 1000 == 0:
                LOGGER.info(f"{tag_count} imported")

    LOGGER.info("Importing pit tags")
    pit_tag_count = 0
    tag_serials = TrtPitTags.objects.values_list("pit_tag_id", flat=True)
    tag_serials = [(t.replace(" ", "").strip(), t) for t in tag_serials]

    for serials in tag_serials:
        # Fast-path skip existing records, no reload.
        if TurtleTag.objects.filter(serial=serials[0], tag_type="pit-tag").exists() and not reload:
            continue
        else:
            wamtram_tag = TrtPitTags.objects.get(pit_tag_id=serials[1])

            if wamtram_tag.custodian_person_id and TrtPersons.objects.filter(person_id=wamtram_tag.custodian_person_id).exists():
                person = TrtPersons.objects.get(person_id=wamtram_tag.custodian_person_id)
                custodian = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                custodian = None
            if wamtram_tag.field_person_id and TrtPersons.objects.filter(person_id=wamtram_tag.field_person_id).exists():
                person = TrtPersons.objects.get(person_id=wamtram_tag.field_person_id)
                field_person = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                field_person = None

            if Turtle.objects.filter(source="wamtram", source_id=wamtram_tag.turtle_id).exists():
                turtle = Turtle.objects.get(source="wamtram", source_id=wamtram_tag.turtle_id)
            else:
                turtle = None

            if wamtram_tag.tag_order_id and TagPurchaseOrder.objects.filter(source_id=wamtram_tag.tag_order_id).exists():
                order = TagPurchaseOrder.objects.get(source_id=wamtram_tag.tag_order_id)
            else:
                order = None

            serial = serials[0]

            if TurtleTag.objects.filter(serial=serial, tag_type="pit-tag").exists():
                if reload:
                    tag = TurtleTag.objects.get(serial=serial, tag_type="pit-tag")
                    tag.turtle = turtle
                    tag.order = order
                    tag.custodian = custodian
                    tag.field_handler = field_person
                    tag.return_date = wamtram_tag.return_date.date() if wamtram_tag.return_date else None
                    tag.return_condition = wamtram_tag.return_condition
                    tag.comments = wamtram_tag.comments
                    tag.batch_number = wamtram_tag.batch_number
                    tag.box_number = wamtram_tag.box_number
                    tag.save()
                else:
                    continue
            else:
                TurtleTag.objects.get_or_create(
                    serial=serial,
                    tag_type="pit-tag",
                    turtle=turtle,
                    order=order,
                    custodian=custodian,
                    field_handler=field_person,
                    return_date=wamtram_tag.return_date.date() if wamtram_tag.return_date else None,
                    return_condition=wamtram_tag.return_condition,
                    comments=wamtram_tag.comments,
                    batch_number=wamtram_tag.batch_number,
                    box_number=wamtram_tag.box_number,
                )
            pit_tag_count += 1
            if pit_tag_count % 1000 == 0:
                LOGGER.info(f"{pit_tag_count} imported")

    LOGGER.info(f"TurtleTag object count: {TurtleTag.objects.count()}")

    LOGGER.info("Importing turtle observations as AnimalEnounters")
    encounter_count = 0
    flipper_tag_count = 0
    pit_tag_count = 0
    measurement_count = 0
    damage_count = 0
    sample_count = 0
    turtle_observation_ids = TrtObservations.objects.values_list("observation_id", flat=True)
    LOGGER.info(f"Checking {turtle_observation_ids.count()} turtle observations")

    for id in turtle_observation_ids:
        # Fast-path skip existing records, no reload.
        if AnimalEncounter.objects.filter(source="wamtram", source_id=id).exists() and not reload:
            continue
        else:
            obs = TrtObservations.objects.get(observation_id=id)

            # If we can't parse a location for this observation, skip it.
            if not obs.get_point():
                continue

            # measurer -> observer
            if obs.measurer_person:
                person = TrtPersons.objects.get(person_id=obs.measurer_person_id)
                observer = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                observer = admin

            # measurer_reporter -> reporter
            if obs.measurer_reporter_person:
                person = TrtPersons.objects.get(person_id=obs.measurer_reporter_person_id)
                reporter = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                reporter = admin

            # tagger_person -> handler
            if obs.tagger_person:
                person = TrtPersons.objects.get(person_id=obs.tagger_person_id)
                handler = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                handler = None

            # reporter_person -> recorder
            if obs.reporter_person:
                person = TrtPersons.objects.get(person_id=obs.reporter_person_id)
                recorder = User.objects.get(name__iexact=person.get_name(), is_active=True)
            else:
                recorder = None

            if Turtle.objects.filter(source="wamtram", source_id=obs.turtle_id).exists():
                turtle = Turtle.objects.get(source="wamtram", source_id=obs.turtle_id)
            else:
                turtle = None

            if obs.activity_code_id and obs.activity_code_id in ACTIVITY_MAP:
                activity = ACTIVITY_MAP[obs.activity_code_id]
            else:
                activity = "na"

            if AnimalEncounter.objects.filter(source="wamtram", source_id=id).exists():
                if reload:
                    encounter = AnimalEncounter.objects.get(source="wamtram", source_id=id)
                    encounter.status = "imported"
                    encounter.where = obs.get_point()
                    encounter.when = obs.get_observation_datetime_utc()
                    encounter.observer = observer
                    encounter.reporter = reporter
                    encounter.encounter_type = "tagging"
                    encounter.comments = obs.comments
                    encounter.taxon = "Cheloniidae"
                    encounter.species = turtle.species if turtle else "unknown"
                    encounter.sex = turtle.sex if turtle else "unknown"
                    encounter.activity = activity
                    encounter.save()
                else:
                    continue
            else:
                encounter, created = AnimalEncounter.objects.get_or_create(
                    source="wamtram",
                    source_id=id,
                    status="imported",
                    where=obs.get_point(),
                    when=obs.get_observation_datetime_utc(),
                    observer=observer,
                    reporter=reporter,
                    encounter_type="tagging",
                    comments=obs.comments,
                    taxon="Cheloniidae",
                    species=turtle.species if turtle else "unknown",
                    sex=turtle.sex if turtle else "unknown",
                )
            encounter_count += 1

            for wamtram_recorded_tag in TrtRecordedTags.objects.filter(observation_id=obs.pk):

                if TurtleTag.objects.filter(serial=wamtram_recorded_tag.tag_id, tag_type="flipper-tag").exists():
                    tag = TurtleTag.objects.get(serial=wamtram_recorded_tag.tag_id, tag_type="flipper-tag")
                else:
                    continue

                status = "resighted"
                if wamtram_recorded_tag.tag_state:
                    if wamtram_recorded_tag.tag_state in ["A1", "AE"]:
                        status = "applied-new"
                    elif wamtram_recorded_tag.tag_state == "RC":
                        status = "reclinched"
                    elif wamtram_recorded_tag.tag_state in ["OO", "R"]:
                        status = "removed"

                if tag.side:
                    if tag.side == "left":
                        location = "flipper-front-left"
                    else:
                        location = "flipper-front-right"
                else:
                    location = "whole"

                TagObservation.objects.get_or_create(
                    source=TagObservation.SOURCE_WAMTRAM2,
                    source_id=wamtram_recorded_tag.recorded_tag_id,
                    encounter=encounter,
                    tag_type="flipper-tag",
                    tag_location=location,
                    name=tag.serial,
                    status=status,
                    handler=handler,
                    recorder=recorder,
                    comments=wamtram_recorded_tag.comments,
                )
                flipper_tag_count += 1

            for wamtram_recorded_pit_tag in TrtRecordedPitTags.objects.filter(observation_id=obs.pk):

                if TurtleTag.objects.filter(serial=wamtram_recorded_pit_tag.pit_tag_id, tag_type="pit-tag").exists():
                    tag = TurtleTag.objects.get(serial=wamtram_recorded_pit_tag.pit_tag_id, tag_type="pit-tag")
                else:
                    continue

                status = "resighted"
                if wamtram_recorded_pit_tag.pit_tag_state:
                    if wamtram_recorded_pit_tag.pit_tag_state_id in ["A1", "AE"]:
                        status = "applied-new"

                TagObservation.objects.get_or_create(
                    source=TagObservation.SOURCE_WAMTRAM2,
                    source_id=wamtram_recorded_pit_tag.recorded_pit_tag_id,
                    encounter=encounter,
                    tag_type="pit-tag",
                    name=tag.serial,
                    status=status,
                    handler=handler,
                    recorder=recorder,
                    comments=wamtram_recorded_pit_tag.comments,
                )
                pit_tag_count += 1

            for wamtram_measurement in TrtMeasurements.objects.filter(observation_id=obs.pk):

                curved_carapace_length_mm = None
                curved_carapace_width_mm = None
                straight_carapace_length_mm = None
                maximum_head_width_mm = None
                body_weight_g = None
                tail_length_plastron_mm = None
                tail_length_vent_mm = None
                tail_length_carapace_mm = None

                if wamtram_measurement.measurement_type_id == "CCL":
                    curved_carapace_length_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "CCW":
                    curved_carapace_width_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "SCL":
                    straight_carapace_length_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "HW":
                    maximum_head_width_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "WEIGHT G":
                    body_weight_g = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "PT":
                    tail_length_plastron_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "VT":
                    tail_length_vent_mm = wamtram_measurement.measurement_value
                elif wamtram_measurement.measurement_type_id == "CT":
                    tail_length_carapace_mm = wamtram_measurement.measurement_value
                else:
                    continue  # Measurement type didn't match any of our known types.

                TurtleMorphometricObservation.objects.get_or_create(
                    source=TurtleMorphometricObservation.SOURCE_WAMTRAM2,
                    source_id=f"{wamtram_measurement.observation_id}_trtmeasurement",
                    encounter=encounter,
                    curved_carapace_length_mm=curved_carapace_length_mm,
                    curved_carapace_width_mm=curved_carapace_width_mm,
                    straight_carapace_length_mm=straight_carapace_length_mm,
                    maximum_head_width_mm=maximum_head_width_mm,
                    body_weight_g=body_weight_g,
                    tail_length_plastron_mm=tail_length_plastron_mm,
                    tail_length_vent_mm=tail_length_vent_mm,
                    tail_length_carapace_mm=tail_length_carapace_mm,
                    handler=handler,
                    recorder=recorder,
                )
                measurement_count += 1

            for wamtram_damage in TrtDamage.objects.filter(observation_id=obs.pk):

                if wamtram_damage.body_part in ["A", "I", "J", "K", "L", "M", "N", "O"]:
                    body_part = "carapace"
                elif wamtram_damage.body_part == "B":
                    body_part = "flipper-front-left"
                elif wamtram_damage.body_part == "C":
                    body_part = "flipper-front-right"
                elif wamtram_damage.body_part == "D":
                    body_part = "flipper-rear-left"
                elif wamtram_damage.body_part == "E":
                    body_part = "flipper-rear-right"
                elif wamtram_damage.body_part == "H":
                    body_part = "head"
                elif wamtram_damage.body_part == "P":
                    body_part = "plastron"
                elif wamtram_damage.body_part == "T":
                    body_part = "tail"
                elif wamtram_damage.body_part == "W":
                    body_part = "whole"
                else:
                    body_part = "other"

                if wamtram_damage.damage_code == "1":
                    damage = "tip-amputated"
                elif wamtram_damage.damage_code == "2":
                    damage = "amputated-from-nail"
                elif wamtram_damage.damage_code == "3":
                    damage = "amputated-half"
                elif wamtram_damage.damage_code == "4":
                    damage = "amputated-entirely"
                elif wamtram_damage.damage_code in ["5", "6"]:
                    damage = "cuts"
                elif wamtram_damage.damage_code == "7":
                    damage = "deformity"
                else:
                    damage = "other"

                TurtleDamageObservation.objects.get_or_create(
                    source=TurtleDamageObservation.SOURCE_WAMTRAM2,
                    source_id=f"{wamtram_damage.observation_id}_trtdamage",
                    encounter=encounter,
                    body_part=body_part,
                    damage_type=damage,
                    damage_age="unknown",
                    description=wamtram_damage.comments,
                )
                damage_count += 1

            for wamtram_sample in TrtSamples.objects.filter(observation_id=obs.pk):

                if wamtram_sample.tissue_type.description == "Blood":
                    sample_type = "blood"
                elif wamtram_sample.tissue_type.description == "Skin":
                    sample_type = "skin"
                elif wamtram_sample.tissue_type.description == "Muscle - Pectoral":
                    sample_type = "muscle"
                elif wamtram_sample.tissue_type.description == "Liver":
                    sample_type = "liver"
                elif wamtram_sample.tissue_type.description == "heart":
                    sample_type = "heart"
                elif wamtram_sample.tissue_type.description == "Kidney":
                    sample_type = "kidney"
                elif wamtram_sample.tissue_type.description == "Gonad":
                    sample_type = "gonad"
                elif wamtram_sample.tissue_type.description == "Fat - depot storage":
                    sample_type = "fat"
                elif wamtram_sample.tissue_type.description == "Brain":
                    sample_type = "brain"
                elif wamtram_sample.tissue_type.description == "Faecal matter":
                    sample_type = "faecal"
                elif wamtram_sample.tissue_type.description == "Epibiota":
                    sample_type = "epibiota"
                elif wamtram_sample.tissue_type.description == "Keratin - Fnail":
                    sample_type = "keratin"
                elif wamtram_sample.tissue_type.description == "Skeletal":
                    sample_type = "bone"
                else:
                    sample_type = "tissue"

                data = {
                    "arsenic": wamtram_sample.arsenic,
                    "selenium": wamtram_sample.selenium,
                    "zinc": wamtram_sample.zinc,
                    "cadmium": wamtram_sample.cadmium,
                    "copper": wamtram_sample.copper,
                    "lead": wamtram_sample.lead,
                    "mercury": wamtram_sample.mercury,
                }

                TissueSampleObservation.objects.get_or_create(
                    source=TissueSampleObservation.SOURCE_WAMTRAM2,
                    source_id=wamtram_sample.sample_id,
                    encounter=encounter,
                    sample_type=sample_type,
                    serial=wamtram_sample.sample_label,
                    description=wamtram_sample.comments,
                    data=data,
                )

                sample_count += 1

            if encounter_count and encounter_count % 1000 == 0:
                LOGGER.info(f"{encounter_count} turtle tagging encounters imported")

    LOGGER.info(f"{encounter_count} turtle tagging encounters imported")
    LOGGER.info(f"{flipper_tag_count} flipper tag observations imported")
    LOGGER.info(f"{pit_tag_count} pit tag observations imported")
    LOGGER.info(f"{measurement_count} measurement observations imported")
    LOGGER.info(f"{damage_count} damage observations imported")
    LOGGER.info(f"{sample_count} sample observations imported")
