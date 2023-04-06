from django.db.models import Max
from django.utils import timezone
from wamtram.models import (
    TrtPlaces,
    TrtPersons,
    TrtEntryBatches,
    TrtTurtles,
    TrtObservations,
    TrtTagOrders,
    TrtTags,
    TrtPitTags,
    TrtMeasurementTypes,
    TrtMeasurements,
    TrtDamage,
    TrtRecordedTags,
    TrtRecordedPitTags,
    TrtSamples,
    TrtIdentification,
)
from users.models import User
from .models import (
    TurtleSpecies,
    Location,
    Place,
    EntryBatch,
    Turtle,
    TurtleObservation,
    TagOrder,
    TurtleTag,
    TurtlePitTag,
    MeasurementType,
    TurtleMeasurement,
    TurtleDamage,
    TurtleTagObservation,
    TurtlePitTagObservation,
    TurtleSample,
    TurtleIdentification,
)


TRT_SPECIES_MAP = {
    'FB': {'scientific_name': 'Natator depressus', 'common_name': 'Flatback Turtle', 'old_species_code': 'F', 'hide_dataentry': False},
    'GN': {'scientific_name': 'Chelonia mydas', 'common_name': 'Green Turtle', 'old_species_code': 'G', 'hide_dataentry': False},
    'HK': {'scientific_name': 'Eretmochelys imbricata', 'common_name': 'Hawksbill Turtle', 'old_species_code': 'H', 'hide_dataentry': False},
    'LB': {'scientific_name': 'Dermochelys coriacea', 'common_name': 'Leatherback Turtle', 'old_species_code': 'LB', 'hide_dataentry': False},
    'LO': {'scientific_name': 'Caretta caretta', 'common_name': 'Loggerhead Turtle', 'old_species_code': 'LO', 'hide_dataentry': False},
    'OR': {'scientific_name': 'Lepidochelys olivacea', 'common_name': 'Olive Ridley Turtle', 'old_species_code': 'OR', 'hide_dataentry': False},
}
TRT_LOCATION_MAP = {
    'AI': {'name': 'Airlie Island'},
    'AR': {'name': 'Ashmore Reef area'},
    'BR': {'name': 'Browse Island'},
    'BW': {'name': 'Barrow Island'},
    'BZ': {'name': 'Brazil coastal'},
    'CD': {'name': 'Cape Domett'},
    'CL': {'name': 'Cape Lambert'},
    'DA': {'name': 'Dampier Archipelago area'},
    'DH': {'name': 'Dirk Hartog Island'},
    'DI': {'name': 'Dorre Island'},
    'EG': {'name': 'Exmouth Gulf area'},
    'EI': {'name': 'Eastern Indian Ocean region'},
    'EM': {'name': 'Eighty Mile Beach - WA'},
    'GA': {'name': 'Gascoyne coastal - Not Ningaloo MP'},
    'GC': {'name': 'Gulf of Carpentaria area'},
    'IN': {'name': 'Indonesian territory'},
    'IR': {'name': 'Imperieuse Reef - Rowley Shoals'},
    'KS': {'name': 'King Sound area'},
    'LA': {'name': 'Lacepede Islands'},
    'LO': {'name': 'Lowendal Islands area'},
    'MB': {'name': 'Monte Bello Islands'},
    'MI': {'name': 'Montgomery Islands (Yawajaba: Yawijibaya people)'},
    'MN': {'name': 'Mundabullangana coast'},
    'MU': {'name': 'Muiron Islands'},
    'NI': {'name': 'Ningaloo MP coastal'},
    'NK': {'name': 'North Kimberley coastal'},
    'NT': {'name': 'Northern Territory coastal'},
    'NW': {'name': 'North West Cape area'},
    'PB': {'name': 'Pilbara offshore & coastal area'},
    'PE': {'name': 'Perth area'},
    'PH': {'name': 'Port Hedland coastal'},
    'QD': {'name': 'Queensland'},
    'RI': {'name': 'Rosemary Island - Dampier Archipelago'},
    'SB': {'name': 'Shark Bay area'},
    'SC': {'name': 'Southern WA coastal'},
    'SE': {'name': 'S-Eastern WA coastal'},
    'SR': {'name': 'Scott Reef'},
    'SW': {'name': 'S-Western WA coastal'},
    'TH': {'name': 'Thevenard Island'},
    'VA': {'name': 'Varanus Island - Lowendals'},
    'WC': {'name': 'Mid-Western WA coastal'},
    'WK': {'name': 'West Kimberley coastal'},
    'XX': {'name': 'Not otherwise assigned'},
}


def import_wamtram(reload=True):
    """Utility function to import/convert data from wamtram (SQL Server) to turtle_data (local).
    The function is idempotent, and may be run multiple times safely without creating duplicate data.

    If `reload` is False, some existing records will be skipped (those having the PK brought across).
    """
    print("Importing species")
    TurtleSpecies.objects.get_or_create(
        scientific_name='Unknown', common_name='Not recorded - uncertain', old_species_code=None, hide_dataentry=False
    )
    for sp in TRT_SPECIES_MAP.values():
        TurtleSpecies.objects.get_or_create(**sp)
    print(f"Object count: {TurtleSpecies.objects.count()}")

    print("Importing locations")
    for loc in TRT_LOCATION_MAP.values():
        Location.objects.get_or_create(**loc)
    print(f"Object count: {Location.objects.count()}")

    print("Importing places")
    for pl in TrtPlaces.objects.all():
        # First, match the newly-created Location obj.
        location = Location.objects.get(name=pl.location_code.location_name)
        Place.objects.get_or_create(
            location=location,
            name=pl.place_name,
            rookery=True if pl.rookery == "Y" else False if pl.rookery == "N" else None,
            beach_approach=pl.beach_approach,
            aspect=pl.aspect,
            point=pl.get_point(),
            comments=pl.comments,
        )
    print(f"Object count: {Place.objects.count()}")

    print("Importing persons")
    for p in TrtPersons.objects.all():
        name = p.get_name()
        if not User.objects.filter(name__iexact=name.lower(), is_active=True).exists():
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
            print(f"POSSIBLE DUPLICATE: {p}")
            return  # Abort
    print(f"Object count: {User.objects.count()}")

    print("Importing entry batches")
    for b in TrtEntryBatches.objects.all():
        if b.entered_person_id:
            try:
                person = TrtPersons.objects.get(person_id=b.entered_person_id)
                name = f"{person.first_name} {person.surname}".strip()
                user = User.objects.get(name__iexact=name.lower(), is_active=True)
            except:
                user = None
        else:
            user = None

        if EntryBatch.objects.filter(pk=b.entry_batch_id).exists() and reload:
            eb = EntryBatch.objects.get(pk=b.entry_batch_id)
            eb.entry_date = b.entry_date.date() if b.entry_date else None
            eb.entered_by = user
            eb.filename = b.filename
            eb.comments = b.comments
            eb.pr_date_convention = b.pr_date_convention
            eb.save()
        else:
            EntryBatch.objects.get_or_create(
                pk=b.entry_batch_id,
                entry_date=b.entry_date.date() if b.entry_date else None,
                entered_by=user,
                filename=b.filename,
                comments=b.comments,
                pr_date_convention=b.pr_date_convention,
            )
    print(f"Object count: {EntryBatch.objects.count()}")

    print("Importing tag orders")
    for o in TrtTagOrders.objects.all():
        if TagOrder.objects.filter(pk=o.tag_order_id).exists() and reload:
            to = TagOrder.objects.get(pk=o.tag_order_id)
            to.order_number = o.order_number
            to.order_date = o.order_date.date() if o.order_date else None
            to.tag_prefix = o.tag_prefix
            to.start_tag_number = o.start_tag_number
            to.end_tag_number = o.end_tag_number
            to.total_tags = o.total_tags
            to.date_received = o.date_received.date() if o.date_received else None
            to.paid_by = o.paid_by
            to.comments = o.comments
            to.save()
        else:
            TagOrder.objects.get_or_create(
                pk=o.tag_order_id,
                order_number=o.order_number,
                order_date=o.order_date.date() if o.order_date else None,
                tag_prefix=o.tag_prefix,
                start_tag_number=o.start_tag_number,
                end_tag_number=o.end_tag_number,
                total_tags=o.total_tags,
                date_received=o.date_received.date() if o.date_received else None,
                paid_by=o.paid_by,
                comments=o.comments,
            )
    print(f"Object count: {TagOrder.objects.count()}")

    print("Importing turtles")
    count = 0
    bobp = User.objects.get(username='bobp')
    admin = User.objects.get(pk=1)
    for t in TrtTurtles.objects.all():
        if t.species_code_id == "?":
            species = TurtleSpecies.objects.get(scientific_name='Unknown')
        elif t.species_code_id == "0":
            species = None
        else:
            species = TurtleSpecies.objects.get(scientific_name=t.species_code.scientific_name)
        if t.location_code:
            location = Location.objects.get(name=TRT_LOCATION_MAP[t.location_code_id]['name'])
        else:
            location = None
        if t.entered_by == 'bobp':
            entered_by = bobp
        else:
            entered_by = admin

        if Turtle.objects.filter(pk=t.turtle_id).exists() and reload:
            tu = Turtle.objects.get(pk=t.turtle_id)
            tu.created = t.date_entered if t.date_entered else timezone.now()
            tu.entered_by = entered_by
            tu.species = species
            tu.sex = t.sex
            tu.status = t.turtle_status.turtle_status if t.turtle_status else None
            tu.name = t.turtle_name
            tu.location = location
            tu.cause_of_death = t.cause_of_death_id if t.cause_of_death else None
            tu.re_entered_population = t.re_entered_population
            tu.comments = t.comments
            tu.original_turtle_id = t.original_turtle_id
            tu.entry_batch = EntryBatch.objects.get(pk=t.entry_batch_id) if t.entry_batch_id else None
            tu.mund_id = t.mund_id
            tu.identification_confidence = t.identification_confidence
            tu.save()
        else:
            Turtle.objects.get_or_create(
                pk=t.turtle_id,
                created=t.date_entered if t.date_entered else timezone.now(),
                entered_by=entered_by,
                species=species,
                status=t.turtle_status.turtle_status if t.turtle_status else None,
                name=t.turtle_name,
                location=location,
                cause_of_death=t.cause_of_death_id if t.cause_of_death else None,
                re_entered_population=t.re_entered_population,
                comments=t.comments,
                original_turtle_id=t.original_turtle_id,
                entry_batch=EntryBatch.objects.get(pk=t.entry_batch_id) if t.entry_batch_id else None,
                mund_id=t.mund_id,
                identification_confidence=t.identification_confidence,
                sex=t.sex,
            )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {Turtle.objects.count()}")

    print("Importing tags")
    count = 0
    for t in TrtTags.objects.all():
        if t.custodian_person_id and TrtPersons.objects.filter(person_id=t.custodian_person_id).exists():
            person = TrtPersons.objects.get(person_id=t.custodian_person_id)
            custodian = User.objects.get(name__iexact=person.get_name(), is_active=True)
        else:
            custodian = None
        if t.field_person_id and TrtPersons.objects.filter(person_id=t.field_person_id).exists():
            person = TrtPersons.objects.get(person_id=t.field_person_id)
            field_person = User.objects.get(name__iexact=person.get_name(), is_active=True)
        else:
            field_person = None
        serial = t.tag_id.replace(" ", "").strip()

        if TurtleTag.objects.filter(serial=serial).exists() and reload:
            tag = TurtleTag.objects.get(serial=serial)
            tag.turtle_id = t.turtle_id
            tag.issue_location = t.issue_location
            tag.custodian = custodian
            tag.side = t.side
            tag.status = t.tag_status.tag_status
            tag.return_date = t.return_date.date() if t.return_date else None
            tag.return_condition = t.return_condition
            tag.comments = t.comments
            tag.field_person = field_person
            tag.tag_order_id = t.tag_order_id if TagOrder.objects.filter(pk=t.tag_order_id).exists() else None
            tag.save()
        else:
            TurtleTag.objects.get_or_create(
                serial=serial,
                turtle_id=t.turtle_id,
                issue_location=t.issue_location,
                custodian=custodian,
                side=t.side,
                status=t.tag_status.tag_status,
                return_date=t.return_date.date() if t.return_date else None,
                return_condition=t.return_condition,
                comments=t.comments,
                field_person=field_person,
                tag_order_id=t.tag_order_id if TagOrder.objects.filter(pk=t.tag_order_id).exists() else None,
            )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleTag.objects.count()}")

    print("Importing pit tags")
    count = 0
    for t in TrtPitTags.objects.all():
        if t.custodian_person_id and TrtPersons.objects.filter(person_id=t.custodian_person_id).exists():
            person = TrtPersons.objects.get(person_id=t.custodian_person_id)
            custodian = User.objects.get(name__iexact=person.get_name(), is_active=True)
        else:
            custodian = None
        if t.field_person_id and TrtPersons.objects.filter(person_id=t.field_person_id).exists():
            person = TrtPersons.objects.get(person_id=t.field_person_id)
            field_person = User.objects.get(name__iexact=person.get_name(), is_active=True)
        else:
            field_person = None
        serial = t.pit_tag_id.replace(" ", "").strip()

        if TurtlePitTag.objects.filter(serial=serial).exists() and reload:
            tag = TurtlePitTag.objects.get(serial=serial)
            tag.turtle_id = t.turtle_id
            tag.issue_location = t.issue_location
            tag.custodian = custodian
            tag.status = t.pit_tag_status
            tag.return_date = t.return_date.date() if t.return_date else None
            tag.return_condition = t.return_condition
            tag.comments = t.comments
            tag.field_person = field_person
            tag.tag_order_id = t.tag_order_id if TagOrder.objects.filter(pk=t.tag_order_id).exists() else None
            tag.batch_number = t.batch_number
            tag.box_number = t.box_number
            tag.save()
        else:
            TurtlePitTag.objects.get_or_create(
                serial=serial,
                turtle_id=t.turtle_id,
                issue_location=t.issue_location,
                custodian=custodian,
                status=t.pit_tag_status,
                return_date=t.return_date.date() if t.return_date else None,
                return_condition=t.return_condition,
                comments=t.comments,
                field_person=field_person,
                tag_order_id=t.tag_order_id if TagOrder.objects.filter(pk=t.tag_order_id).exists() else None,
                batch_number=t.batch_number,
                box_number=t.box_number,
            )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtlePitTag.objects.count()}")

    print("Importing observations")
    count = 0
    for obs in TrtObservations.objects.all():
        if obs.measurer_person:
            measurer = User.objects.get(name__iexact=obs.measurer_person.get_name(), is_active=True)
        else:
            measurer = None
        if obs.measurer_reporter_person:
            measurer_reporter = User.objects.get(name__iexact=obs.measurer_reporter_person.get_name(), is_active=True)
        else:
            measurer_reporter = None
        if obs.tagger_person:
            tagger = User.objects.get(name__iexact=obs.tagger_person.get_name(), is_active=True)
        else:
            tagger = None
        if obs.reporter_person:
            reporter = User.objects.get(name__iexact=obs.reporter_person.get_name(), is_active=True)
        else:
            reporter = None
        if obs.place_code and Place.objects.filter(name=obs.place_code.place_name).count() == 1:
            place = Place.objects.get(name=obs.place_code.place_name)
        else:
            place = None  # There are a couple of places with identical names but different locations.
        if obs.entered_by_person:
            entered_by = User.objects.get(name__iexact=obs.entered_by_person.get_name(), is_active=True)
        else:
            entered_by = None
        if obs.clutch_completed and obs.clutch_completed == 'y':
            clutch_completed = 'Y'
        elif obs.clutch_completed and obs.clutch_completed == 'n':
            clutch_completed = 'U'
        else:
            clutch_completed = 'U'

        if TurtleObservation.objects.filter(pk=obs.observation_id).exists() and reload:
            o = TurtleObservation.objects.get(pk=obs.observation_id)
            o.created = obs.date_entered if obs.date_entered else timezone.now()
            o.entered_by = entered_by
            o.turtle_id = obs.turtle_id
            o.observed = obs.get_observation_datetime_utc()
            o.observation_date_old = obs.observation_date_old.date() if obs.observation_date_old else None
            o.alive = True if obs.alive == "Y" else False if obs.alive == "N" else None
            o.measurer = measurer
            o.measurer_reporter = measurer_reporter
            o.tagger = tagger
            o.reporter = reporter
            o.place = place
            o.place_description = obs.place_description
            o.point = obs.get_point()
            o.activity = obs.activity_code
            o.beach_position = obs.beach_position_code.beach_position_code if obs.beach_position_code else None
            o.condition = obs.condition_code.condition_code if obs.condition_code else None
            o.nesting = True if obs.nesting == "Y" else False if obs.nesting == "N" else None
            o.clutch_completed = clutch_completed
            o.number_of_eggs = obs.number_of_eggs
            o.egg_count_method = obs.egg_count_method.egg_count_method if obs.egg_count_method else None
            o.action_taken = obs.action_taken
            o.comments = obs.comments
            o.original_observation_id = obs.original_observation_id
            o.entry_batch = EntryBatch.objects.get(pk=obs.entry_batch_id) if obs.entry_batch else None
            o.comment_fromrecordedtagstable = obs.comment_fromrecordedtagstable
            o.scars_left = obs.scars_left
            o.scars_right = obs.scars_right
            o.transferid = obs.transferid
            o.mund = obs.mund
            o.scars_left_scale_1 = obs.scars_left_scale_1
            o.scars_left_scale_2 = obs.scars_left_scale_2
            o.scars_left_scale_3 = obs.scars_left_scale_3
            o.scars_right_scale_1 = obs.scars_right_scale_1
            o.scars_right_scale_2 = obs.scars_right_scale_2
            o.scars_right_scale_3 = obs.scars_right_scale_3
            o.cc_length_not_measured = obs.cc_length_not_measured
            o.cc_notch_length_not_measured = obs.cc_notch_length_not_measured
            o.cc_width_not_measured = obs.cc_width_not_measured
            o.tagscarnotchecked = obs.tagscarnotchecked
            o.didnotcheckforinjury = obs.didnotcheckforinjury
            o.date_convention = obs.date_convention
            o.status = obs.observation_status
            o.corrected_date = obs.corrected_date.date() if obs.corrected_date else None
            o.save()
        else:
            TurtleObservation.objects.create(
                pk=obs.observation_id,
                created=obs.date_entered if obs.date_entered else timezone.now(),
                entered_by=entered_by,
                turtle_id=obs.turtle_id,
                observed=obs.get_observation_datetime_utc(),
                observation_date_old=obs.observation_date_old.date() if obs.observation_date_old else None,
                alive=True if obs.alive == "Y" else False if obs.alive == "N" else None,
                measurer=measurer,
                measurer_reporter=measurer_reporter,
                tagger=tagger,
                reporter=reporter,
                place=place,
                place_description=obs.place_description,
                point=obs.get_point(),
                activity=obs.activity_code,
                beach_position=obs.beach_position_code.beach_position_code if obs.beach_position_code else None,
                condition=obs.condition_code.condition_code if obs.condition_code else None,
                nesting=True if obs.nesting == "Y" else False if obs.nesting == "N" else None,
                clutch_completed=clutch_completed,
                number_of_eggs=obs.number_of_eggs,
                egg_count_method=obs.egg_count_method.egg_count_method if obs.egg_count_method else None,
                action_taken=obs.action_taken,
                comments=obs.comments,
                original_observation_id=obs.original_observation_id,
                entry_batch=EntryBatch.objects.get(pk=obs.entry_batch_id) if obs.entry_batch else None,
                comment_fromrecordedtagstable=obs.comment_fromrecordedtagstable,
                scars_left=obs.scars_left,
                scars_right=obs.scars_right,
                transferid=obs.transferid,
                mund=obs.mund,
                scars_left_scale_1=obs.scars_left_scale_1,
                scars_left_scale_2=obs.scars_left_scale_2,
                scars_left_scale_3=obs.scars_left_scale_3,
                scars_right_scale_1=obs.scars_right_scale_1,
                scars_right_scale_2=obs.scars_right_scale_2,
                scars_right_scale_3=obs.scars_right_scale_3,
                cc_length_not_measured=obs.cc_length_not_measured,
                cc_notch_length_not_measured=obs.cc_notch_length_not_measured,
                cc_width_not_measured=obs.cc_width_not_measured,
                tagscarnotchecked=obs.tagscarnotchecked,
                didnotcheckforinjury=obs.didnotcheckforinjury,
                date_convention=obs.date_convention,
                status=obs.observation_status,
                corrected_date=obs.corrected_date.date() if obs.corrected_date else None,
            )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleObservation.objects.count()}")

    print("Importing measurement types")
    for t in TrtMeasurementTypes.objects.all():
        MeasurementType.objects.get_or_create(
            short_desc=t.measurement_type,
            description=t.description,
            unit=t.measurement_units,
            minimum_value=t.minimum_value,
            maximum_value=t.maximum_value,
            comments=t.comments,
        )
    print(f"Object count: {MeasurementType.objects.count()}")

    print("Importing measurements")
    count = 0
    for m in TrtMeasurements.objects.all():
        # Skip invalid data.
        if not TurtleObservation.objects.filter(pk=m.observation.observation_id).exists():
            print(f"Skipped TrtMeasurements object referencing TrtObservations {m.observation}")
            continue
        obs = TurtleObservation.objects.get(pk=m.observation.observation_id)
        mtype = MeasurementType.objects.get(short_desc=m.measurement_type.measurement_type)
        TurtleMeasurement.objects.get_or_create(
            observation=obs,
            measurement_type=mtype,
            value=m.measurement_value,
            comments=m.comments,
        )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleMeasurement.objects.count()}")

    print("Importing turtle damage records")
    count = 0
    for d in TrtDamage.objects.all():
        if not TurtleObservation.objects.filter(pk=d.observation_id).exists():
            print(f"Skipped TrtDamage object referencing TrtObservations {d.observation}")
            continue
        TurtleDamage.objects.get_or_create(
            observation_id=d.observation_id,
            body_part=d.body_part_id,
            damage=d.damage_code_id,
            cause=d.damage_cause_code_id,
            comments=d.comments,
        )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleDamage.objects.count()}")

    print("Importing turtle tag observation records")
    count = 0
    for t in TrtRecordedTags.objects.all():
        if not TurtleObservation.objects.filter(pk=t.observation_id).exists():
            print(f"Skipped TrtRecordedTags object referencing TrtObservations {t.observation}")
            continue
        if not TurtleTag.objects.filter(serial=t.tag_id).exists():
            print(f"Skipped TrtRecordedTags object referencing TurtleTag {t.tag_id}")
            continue
        tag = TurtleTag.objects.get(serial=t.tag_id)
        TurtleTagObservation.objects.get_or_create(
            tag=tag,
            observation_id=t.observation_id,
            status=t.tag_state,
            position=t.tag_position,
            barnacles=t.barnacles,
            comments=t.comments,
        )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleTagObservation.objects.count()}")

    print("Importing turtle pit tag observation records")
    count = 0
    for t in TrtRecordedPitTags.objects.all():
        if not TurtleObservation.objects.filter(pk=t.observation_id).exists():
            print(f"Skipped TrtRecordedPitTags object referencing TrtObservations {t.observation_id}")
            continue
        if not TurtlePitTag.objects.filter(serial=t.pit_tag_id).exists():
            print(f"Skipped TrtRecordedPitTags object referencing TurtlePitTag {t.pit_tag_id}")
            continue
        pit_tag = TurtlePitTag.objects.get(serial=t.pit_tag_id)
        TurtlePitTagObservation.objects.get_or_create(
            tag=pit_tag,
            observation_id=t.observation_id,
            status=t.pit_tag_state.pit_tag_state,
            position=t.pit_tag_position,
            checked=t.checked,
            comments=t.comments,
        )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtlePitTagObservation.objects.count()}")

    print("Importing turtle identification records")
    for t in TrtIdentification.objects.all():
        turtle = Turtle.objects.get(pk=t.turtle_id)
        TurtleIdentification.objects.get_or_create(
            turtle=turtle,
            identification_type=t.identification_type.identification_type,
            identifier=t.identifier,
            comments=t.comments,
        )
    print(f"Object count: {TurtleIdentification.objects.count()}")

    print("Importing turtle sample records")
    count = 0
    for t in TrtSamples.objects.filter(observation_id__isnull=False):
        observation = TurtleObservation.objects.get(pk=t.observation_id)
        TurtleSample.objects.get_or_create(
            observation=observation,
            tissue_type=t.tissue_type.tissue_type,
            label=t.sample_label,
            sample_date=t.sample_date.date() if t.sample_date else None,
            arsenic=t.arsenic,
            selenium=t.selenium,
            zinc=t.zinc,
            cadmium=t.cadmium,
            copper=t.copper,
            lead=t.lead,
            mercury=t.mercury,
            comments=t.comments,
        )
        count += 1
        if count % 1000 == 0:
            print(f"{count} imported")
    print(f"Object count: {TurtleSample.objects.count()}")

    print("Complete")
    print("Set sequence values for: EntryBatch, TagOrder, Turtle, TurtleObservation")
    entrybatch_id_max = EntryBatch.objects.aggregate(Max('pk'))['pk__max']
    print(f"SELECT setval('tagging_entrybatch_id_seq', {entrybatch_id_max}, true);")
    tagorder_id_max = TagOrder.objects.aggregate(Max('pk'))['pk__max']
    print(f"SELECT setval('tagging_tagorder_id_seq', {tagorder_id_max}, true);")
    turtle_id_max = Turtle.objects.aggregate(Max('pk'))['pk__max']
    print(f"SELECT setval('tagging_turtle_id_seq', {turtle_id_max}, true);")
    turtleobservation_id_max = TurtleObservation.objects.aggregate(Max('pk'))['pk__max']
    print(f"SELECT setval('tagging_turtleobservation_id_seq', {turtleobservation_id_max}, true);")
    ident_id_max = TurtleIdentification.objects.aggregate(Max('pk'))['pk__max']
    print(f"SELECT setval('tagging_turtleidentification_id_seq', {ident_id_max}, true);")
