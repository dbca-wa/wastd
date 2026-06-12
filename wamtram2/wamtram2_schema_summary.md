# WAMTRAM2 Legacy Database Schema Summary

**Last updated:** 12-Jun-2026

## Overview

**WAMTRAM2** is a read-only Django ORM bridge to the **WAMTRAM** legacy database—an old MSSQL system that predates WAStD. The models are auto-generated from the existing MSSQL schema and represent ~30+ years of accumulated turtle tagging and observation data.

### Key Characteristics

- **Read-only access** via `Wamtram2Router` database router (segregated database connection)
- **Auto-generated models** from existing MSSQL database schema (migrations not managed by Django)
- **Unmanaged Django models** (`managed = False`)—no `makemigrations` or `migrate` applies to these
- **Legacy naming conventions**—all-uppercase column names (e.g., `TURTLE_ID`, `OBSERVATION_ID`)
- **Batch data import model** supporting complex entry workflows
- **Tag lifecycle tracking**—flipper tags and PIT tags with full status history
- **Opportunistic observation model**—turtle sightings, measurements, damage documentation

### Purpose

Enable WAStD to:

- Access historical turtle and observation data from WAMTRAM
- Support data migration workflows (import/reconcile with new WAStD records)
- Avoid data duplication when re-importing legacy datasets
- Query historical tag lifecycles and animal sighting histories

---

## Core Model Hierarchy

### **TrtTurtles** (Central animal entity)

_Individual animal records tracked across multiple sightings_

**Key Fields:**

- `turtle_id` (AutoField): System-assigned unique ID
- `species_code` (FK → TrtSpecies): Species classification
- `identification_confidence` (CharField): Certainty of species ID
- `sex` (CharField): M/F/I (Indeterminate)
- `turtle_status` (FK → TrtTurtleStatus): Current status classification
- `location_code` (FK → TrtLocations): Associated location
- `cause_of_death` (FK → TrtCauseOfDeath): If applicable (null if alive)
- `re_entered_population` (CharField): Release status flag
- `comments` (CharField): Notes
- `entered_by` / `date_entered`: Audit trail
- `tag` / `turtle_name`: Alternative identifiers
- `mund_id`: MUNDG identifier (possibly mapping to another system)

**Relationships:**

- Has many `TrtObservations` (reverse: `observation.turtle`)
- Has many `TrtTags` (reverse: `tag.turtle`)
- Has many `TrtPitTags` (reverse: `pittag.turtle`)
- Belongs to `TrtSpecies`, `TrtTurtleStatus`, `TrtLocations`, `TrtCauseOfDeath`

---

### **TrtObservations** (Sighting records)

_Each time a turtle was encountered/observed_

**Key Fields:**

- `observation_id` (AutoField): Unique observation ID
- `turtle` (FK → TrtTurtles, CASCADE): The observed animal
- `observation_date` (DateTime): When observed
- `observation_time` (DateTime): Time component (legacy schema redundancy)
- `observation_date_old` (DateTime): Historical field (deprecated)
- `alive` (FK → TrtYesNo): Y/N flag
- `place_code` (FK → TrtPlaces): General location
- `place_description` (CharField): Free-text location
- `datum_code` (FK → TrtDatumCodes): Coordinate system
- `latitude`, `longitude` (Float): DD coordinates
- `latitude_degrees/minutes/seconds`, `longitude_degrees/minutes/seconds`: Legacy DMS format
- `zone`, `easting`, `northing`: UTM coordinates (alternative)
- `activity_code` (FK → TrtActivities): What activity was occurring
- `beach_position_code` (FK → TrtBeachPositions): Beach position
- `condition_code` (FK → TrtConditionCodes): Animal condition
- `nesting` (FK → TrtYesNo): Was animal nesting?
- `clutch_completed` (FK → TrtYesNo): Clutch status
- `number_of_eggs` (SmallInt): Eggs laid/observed
- `egg_count_method` (FK → TrtEggCountMethods): How eggs were counted
- `measurements` (CharField): Indicator flag (measurements recorded?)
- `action_taken` (CharField): Intervention documentation
- `comments` (TextField): Free-text notes
- `entered_by` / `date_entered`: Audit trail
- `entry_batch` (FK → TrtEntryBatches): Batch import tracking

**Observer Tracking:**

- `measurer_person` (FK → TrtPersons): Who took measurements
- `measurer_reporter_person` (FK → TrtPersons): Who recorded measurements
- `tagger_person` (FK → TrtPersons): Who applied tags
- `reporter_person` (FK → TrtPersons): Who reported sighting

**Relationships:**

- Belongs to `TrtTurtles`, `TrtPlaces`, `TrtActivities`, `TrtBeachPositions`, etc.
- Has one `TrtDamage` (reverse: `damage.observation`)
- Has many `TrtMeasurements` (reverse: `measurement.observation`)
- Has many `TrtRecordedTags` (reverse: `recorded_tag.observation`)
- Has many `TrtRecordedPitTags` (reverse: `recorded_pittag.observation`)
- Has many `TrtRecordedIdentifications` (reverse: `recorded_id.observation`)
- Belongs to `TrtEntryBatches` (for data lineage)

---

### **TrtDataEntry** (Batch data entry records)

_Intermediate records from bulk data import workflows_

**Key Fields:**

- `data_entry_id` (AutoField): Entry record ID
- `entry_batch` (FK → TrtEntryBatches): Batch this entry belongs to
- `user_entry_id` (IntegerField): Manual ID from operator
- `turtle_id` (FK → TrtTurtles, nullable): Linked animal (if known)
- `observation_id` (FK → TrtObservations, nullable): Linked observation (if known)
- `do_not_process` (Boolean): Skip flag
- `place_code` (FK → TrtPlaces): Location
- `alive` (FK → TrtYesNo): Alive status
- `sex` (CharField): Animal sex
- `activity_code` (FK → TrtActivities): Activity classification
- `date_of_sighting` (DateTime): Sighting date
- `comments` (TextField): Notes

**Tag Tracking (recaptures):**

- `recapture_left_tag_id`, `recapture_left_tag_id_2` (FK → TrtTags): Left flipper tags found
- `recapture_right_tag_id`, `recapture_right_tag_id_2` (FK → TrtTags): Right flipper tags found
- `recapture_pittag_id` (FK → TrtPitTags): PIT tag found
- `other_left_tag`, `other_right_tag` (CharField): Non-standard tags

**Tag Tracking (new tags applied):**

- `new_left_tag_id`, `new_left_tag_id_2` (FK → TrtTags): New left flipper tags
- `new_right_tag_id`, `new_right_tag_id_2` (FK → TrtTags): New right flipper tags
- `new_pittag_id` (FK → TrtPitTags): New PIT tag
- `new_tag_position` (choices): Scale position (1, 2, or 3)

**Measurements & Identifiers:**

- `measurements_*`: Various morphometric fields (length, width, depth, mass, etc.)
- `identification_confidence` (CharField): Species ID confidence

**Use Case:** Intermediate data capture during bulk imports; allows reconciliation before finalizing observation records

---

### **TrtTags** (Flipper tag records)

_Individual flipper tag lifecycle tracking_

**Key Fields:**

- `tag_id` (CharField, PK): The tag's serial number (e.g., "A123")
- `tag_order_id` (IntegerField): Order reference
- `issue_location` (CharField): Where tag was issued
- `custodian_person` (FK → TrtPersons): Tag custodian/manager
- `turtle` (FK → TrtTurtles, nullable): Associated animal (if applied)
- `side` (CharField): L/R (left/right flipper)
- `tag_status` (FK → TrtTagStatus): Current status (new, applied, recaptured, lost, etc.)
- `return_date` (DateTime): When tag returned/recovered
- `return_condition` (CharField): Condition upon return
- `comments` (CharField): Notes
- `field_person_id` (IntegerField): Handler ID

**Tag Lifecycle:** Tracked through `TrtTagOrders` → `TrtTagStatus` transitions

**Relationships:**

- Belongs to `TrtTurtles` (if applied)
- Belongs to `TrtPersons` (custodian)
- Belongs to `TrtTagStatus`
- Referenced by `TrtDataEntry` (recapture/new tag fields)
- Referenced by `TrtRecordedTags`

---

### **TrtPitTags** (PIT tag records)

_Passive Integrated Transponder tag lifecycle_

**Key Fields:**

- `pittag_id` (CharField, PK): PIT tag number
- `issue_location` (CharField): Issued location
- `pit_tag_status` (FK → TrtPitTagStatus): Current status
- `turtle` (FK → TrtTurtles, nullable): Associated animal
- `comments` (CharField): Notes

**Relationships:**

- Belongs to `TrtTurtles` (if applied)
- Referenced by `TrtDataEntry` (recapture/new tag fields)
- Referenced by `TrtRecordedPitTags`

---

### **TrtMeasurements** (Morphometric data)

_Individual size/mass measurements from observations_

**Key Fields:**

- `measurement_id` (AutoField): Measurement ID
- `observation` (FK → TrtObservations): Associated observation
- `measurement_type` (FK → TrtMeasurementTypes): What was measured
- `value` (Float): Measurement value
- `measurement_unit` (CharField): Unit (mm, g, etc.)

**Related Types:** See `TrtMeasurementTypes` (defines measurement categories)

---

### **TrtDamage** (Injury documentation)

_Physical damage or injury to observed turtle_

**Key Fields:**

- `observation` (OneToOneFK → TrtObservations, CASCADE): The observation with damage
- `body_part` (FK → TrtBodyParts): Anatomical location
- `damage_code` (FK → TrtDamageCodes): Damage type/severity
- `damage_cause_code` (FK → TrtDamageCauseCodes): Cause classification
- `comments` (CharField): Description

**Unique Constraint:** `(observation, body_part)` — one damage record per body part per observation

---

## Lookup/Reference Tables

### **TrtSpecies** (Species codes)

- `species_code` (Char, PK): Code (FB=Flatback, HK=Hawksbill, LO=Loggerhead, GN=Green, LB=Leatherback, OR=Olive Ridley)
- `scientific_name` (Char): Latin name
- `common_name` (Char): English name
- `old_species_code` (Char): Legacy alias
- `hide_dataentry` (Boolean): Exclude from data entry

**Custom manager:** `TrtSpeciesManager` orders by priority (Flatback, Hawksbill, etc. first)

---

### **TrtPersons** (People/staff records)

- `person_id` (AutoField): ID
- `person_first_name` (Char): First name
- `person_last_name` (Char): Last name
- `person_full_name` (Char): Full name (computed)

_Used as FK on observations, tags, measurements to track who did what_

---

### **TrtPlaces** (Specific locations)

- `place_code` (Char, PK): Code
- `place_name` (Char): Location name
- `location_code` (FK → TrtLocations): Higher-level area

---

### **TrtLocations** (General areas/regions)

- `location_code` (Char, PK): Code
- `description` (Char): Location description
- `area_sqkm` (Float): Area in km²

---

### **TrtActivities** (Activity codes)

- `activity_code` (Char, PK): Code
- `description` (Char): Activity type (tagging, stranding, nesting, etc.)
- `nesting` (Char): Nesting-related indicator
- `new_code` (Char): Updated code mapping
- `display_observation` (Boolean): Show in observations

---

### **TrtBeachPositions** (Beach habitat positions)

- `beach_position_code` (Char, PK): Code
- `description` (Char): Position description
- `new_code` (Char): Updated code

---

### **TrtConditionCodes** (Animal health/condition)

- `condition_code` (Char, PK): Code
- `description` (Char): Condition description

---

### **TrtBodyParts** (Anatomical locations)

- `body_part` (Char, PK): Code
- `description` (Char): Body part name
- `flipper` (Boolean): Is it a flipper?

---

### **TrtDamageCodes** (Damage/injury types)

- `damage_code` (Char, PK): Code
- `description` (Char): Damage type
- `new_code` (Char): Updated code

---

### **TrtDamageCauseCodes** (Injury cause classifications)

- `damage_cause_code` (Char, PK): Code
- `description` (Char): Cause description

---

### **TrtCauseOfDeath** (Mortality reasons)

- `cause_of_death` (Char, PK): Code
- `description` (Char): Cause description

---

### **TrtTagStatus** (Flipper tag lifecycle states)

- `tag_status` (Char, PK): Code
- `description` (Char): Status (new, applied, recaptured, lost, returned, etc.)

---

### **TrtPitTagStatus** (PIT tag lifecycle states)

- `pit_tag_status_id` (Char, PK): Code
- `description` (Char): Status

---

### **TrtYesNo** (Boolean flags)

- `code` (Char, PK): Y/N
- `description` (Char): Yes/No

---

### **TrtDatumCodes** (Coordinate systems)

- `datum_code` (Char, PK): Code
- `description` (Char): Datum/projection

---

### **TrtMeasurementTypes** (Measurement categories)

- `measurement_type_id` (IntegerField, PK): ID
- `description` (Char): Measurement name (carapace length, plastron width, etc.)

---

### **TrtEggCountMethods** (Egg counting techniques)

- `egg_count_method_id` (Char, PK): Code
- `description` (Char): Method name

---

### **TrtTurtleStatus** (Animal status classifications)

- `turtle_status` (Char, PK): Code
- `description` (Char): Status (alive, dead, unknown, etc.)
- `new_tag_list` (Boolean): Include in new tag list?

---

### **TrtTagOrders** (Tag supply/ordering)

- `tag_order_id` (IntegerField, PK): Order ID
- `tag_type` (Char): Tag type code
- `number_of_tags` (SmallInt): Quantity ordered

---

### **TrtEntryBatches** (Data import batches)

- `entry_batch_id` (AutoField): Batch ID
- `date_created` (DateTime): When batch created
- `entered_by_person_id` (FK → TrtPersons): Who submitted
- `entry_batch_status` (Char): Status (new, imported, complete, etc.)
- `entry_batch_name` (Char): Batch identifier
- `comments` (TextField): Batch notes

---

### **TrtIdentificationTypes** (ID verification methods)

- `identification_type_id` (Char, PK): Code
- `description` (Char): ID method (tag, photo, genetic, etc.)

---

### **TrtRecordedIdentifications** (ID verifications per observation)

- `observation` (FK → TrtObservations): Observation
- `identification_type` (FK → TrtIdentificationTypes): How identified
- `identification_confidence` (Char): Certainty level

---

### **TrtRecordedTags** (Flipper tags observed)

- `observation` (FK → TrtObservations): Observation
- `tag_id` (FK → TrtTags): Tag found
- `tag_position` (Char): L/R/unknown

---

### **TrtRecordedPitTags** (PIT tags observed)

- `observation` (FK → TrtObservations): Observation
- `pittag_id` (FK → TrtPitTags): PIT tag found
- `pit_tag_status_id` (FK → TrtPitTagStatus): Status at observation

---

### **TrtSighting** (Sightings view/table)

_Denormalized sighting records (possibly a view)_

- Flattened data from `TrtObservations` and related tables
- Contains location, species, condition, tag info in single record
- Likely used for reporting/analysis

---

### **TrtDataChanged** (Audit trail)

_Tracks modifications to records over time_

- `record_id`: Which record was changed
- `table_name`: Which table
- `changed_by`: Who changed it
- `date_changed`: When changed
- `old_value`: Previous value
- `new_value`: New value

---

### **TrtNesting** (Nesting records)

- Supplementary nesting-specific data

---

### **TrtDocuments** (Attached files/documents)

- `document_id` (AutoField)
- `related_table` (Char): Which table it relates to
- `related_id` (IntegerField): Record ID in that table
- `document_type` (FK → TrtDocumentTypes)
- `attachment` (FileField): File content

---

### **TrtSamples** (Tissue/genetic samples)

- `sample_id` (AutoField)
- `observation` (FK → TrtObservations): Observation from which sample taken
- `tissue_type` (FK → TrtTissueTypes): Sample classification

---

### **TrtTissueTypes** (Sample classification)

- `tissue_type_id` (Char, PK)
- `description` (Char)

---

## Data Flow & Relationships

```
TrtEntryBatches (batch imports)
  └─ contains TrtDataEntry (intermediate records)
      ├─ links to TrtTurtles (if ID'd during entry)
      ├─ links to TrtObservations (if reconciled)
      └─ tracks tags being applied/recaptured

TrtTurtles (central animals)
  ├─ has many TrtObservations (sightings)
  │   ├─ has one TrtDamage (injury)
  │   ├─ has many TrtMeasurements (morphometrics)
  │   ├─ has many TrtRecordedTags (tags observed)
  │   ├─ has many TrtRecordedPitTags (PIT tags observed)
  │   └─ has many TrtRecordedIdentifications (ID methods)
  ├─ has many TrtTags (flipper tags applied)
  └─ has many TrtPitTags (PIT tags applied)

TrtTags (flipper tags)
  ├─ tracks lifecycle via TrtTagStatus
  ├─ belongs to TrtTurtles (if applied)
  ├─ belongs to TrtPersons (custodian)
  └─ referenced by TrtObservations/TrtDataEntry during recaptures

TrtPitTags (PIT tags)
  ├─ tracks lifecycle via TrtPitTagStatus
  ├─ belongs to TrtTurtles (if applied)
  └─ referenced by TrtObservations/TrtDataEntry during recaptures

Reference Tables (lookup codes)
  ├─ TrtSpecies → species classification
  ├─ TrtPlaces → specific locations
  ├─ TrtLocations → general areas
  ├─ TrtActivities → activity classification
  ├─ TrtBeachPositions → beach habitat
  ├─ TrtConditionCodes → animal health
  ├─ TrtBodyParts → anatomy
  ├─ TrtDamageCodes / TrtDamageCauseCodes → injury
  └─ ... [many more lookups]
```

---

## Key Technical Patterns

### **Database Router** (`Wamtram2Router`)

Routes all wamtram2 app queries to separate MSSQL database:

```python
def db_for_read(self, model, **hints):
    if model._meta.app_label == "wamtram2":
        return "wamtram2"  # Read from MSSQL
    return None

def db_for_write(self, model, **hints):
    if model._meta.app_label == "wamtram2":
        return "wamtram2"  # Write to MSSQL (rarely used)
    return None

def allow_migrate(self, db, app_label, **hints):
    return None  # Never auto-migrate wamtram2 models
```

### **Auto-Generated Models** (`managed = False`)

- All models have `managed = False` in Meta
- Django does not attempt to create/alter/delete tables
- Schema controlled by legacy MSSQL database maintainers
- Field names explicitly mapped to uppercase DB columns via `db_column`

### **Legacy Coordinate Systems**

Multiple coordinate formats in `TrtObservations`:

- **Decimal Degrees**: `latitude`, `longitude` (modern)
- **Degrees/Minutes/Seconds**: `latitude_degrees`, `latitude_minutes`, `latitude_seconds` (legacy)
- **UTM**: `zone`, `easting`, `northing` (alternative)

### **Nullable Foreign Keys**

Many FKs are nullable (`.set_null`), allowing observations without full context:

```python
turtle_id = models.ForeignKey(TrtTurtles, SET_NULL, null=True)
```

Enables recording sightings of unidentified animals.

### **Tag Batch Import Pattern**

`TrtDataEntry` acts as intermediate staging for bulk imports:

1. Parse raw data into `TrtDataEntry` records
2. Operator reviews/reconciles in admin
3. Batch marked as complete
4. Script processes batch → creates/updates `TrtTurtles`, `TrtObservations`, `TrtTags`

---

## Integration with WAStD

### **Data Migration**

- WAStD queries `TrtObservations` to identify historical records
- Matches on `source_id` (WAMTRAM observation ID) to avoid duplication
- Creates new `observations.Encounter` + `observations.Observation` records
- Preserves `source = "wamtram"` + `source_id = old_observation_id` for audit

### **Legacy Compatibility**

- WAStD inherits field mappings (e.g., `TrtSpecies.common_name` → `AnimalEncounter.species`)
- Maintains tag name consistency (e.g., WAMTRAM tag IDs used as `TagObservation.name`)
- Supports historical queries ("When was this tag last recaptured?") joining across databases

### **Read-Only Philosophy**

- WAMTRAM2 is never written to from WAStD (except legacy data import scripts)
- All new data enters via WAStD's own models (`observations.*`)
- Prevents accidental data corruption in legacy system

---

## Common Queries

### **Find all observations of a turtle:**

```python
turtle = TrtTurtles.objects.get(turtle_id=123)
observations = turtle.trtobservations_set.all().order_by('-observation_date')
```

### **Get tag history (flipper tags):**

```python
tags = TrtTags.objects.filter(turtle_id=123)
for tag in tags:
    print(f"Tag {tag.tag_id}: {tag.tag_status} (applied {tag.})
```

### **Find animals in a location:**

```python
obs = TrtObservations.objects.filter(
    place_code__location_code='XX'
).select_related('turtle')
```

### **Get measurements from an observation:**

```python
obs = TrtObservations.objects.get(observation_id=456)
measurements = obs.trtmeasurements_set.all()
```

---

## Summary

WAMTRAM2 implements a **normalized, multi-table design** suitable for:

- ✅ Historical data archival (30+ years of turtle research)
- ✅ Complex tag lifecycle management
- ✅ Bulk data import workflows with intermediate staging
- ✅ Multiple coordinate system support (legacy migration)
- ✅ Denormalized views for reporting (e.g., `TrtSighting`)
- ✅ Audit trails and change tracking

**Critical Design Note:** This is a **read-only bridge** to a legacy system. All new data collection uses WAStD's modern `observations` app models. WAMTRAM2 serves as a historical reference and data source for migration workflows only.
