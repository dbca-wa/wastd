# WAStD Observations Data Schema Summary

**Last updated**: 12-Jun-2026

## Overview

The **observations** app is the core data model for WAStD. It records turtle and marine mammal encounter data with a flexible, hierarchical design using Django polymorphic models.

### Key Design Principles

- **Encounters** represent discrete events where observations are recorded
- **Observations** are specific data points recorded during an Encounter
- **Polymorphic inheritance** allows specialized subtypes without database table proliferation
- **QA/Curation workflow** manages data quality through state transitions
- **Spatial indexing** (PostGIS) supports location-based queries
- **Legacy source tracking** preserves data lineage from WAMTRAM and other systems

---

## Core Model Hierarchy

### **Encounter** (PolymorphicModel)

_Base class for all observation events_

**Key Fields:**

- `when` (DateTime, UTC): Observation timestamp
- `where` (PointField, WGS84): GPS location
- `location_accuracy` / `location_accuracy_m`: Precision estimate (10m–10km)
- `observer` (FK → User): Person performing observation
- `reporter` (FK → User): Person recording data (field notes)
- `source` + `source_id` (unique_together): Legacy system identifier
- `status` (FSMField): QA workflow state (new → imported → manual_input → proofread → curated → published, plus flagged/rejected)
- `encounter_type`: Classification (stranding, tagging, inwater, nest, tracks, tag-management, logger, disturbance, other)
- `campaign` (FK → Campaign): Related campaign (auto-linked)
- `survey` (FK → Survey): Related survey
- `area` (FK → Area): General locality
- `site` (FK → Area): Specific surveyed site
- `name`: Auto-generated subject identifier (e.g., earliest tag ID for an animal)
- `comments`: Free-text notes
- `as_html`: Cached HTML representation

**Relationships:**

- Has many `Observation` objects (reverse: `encounter.observations`)
- Belongs to optional `Campaign`, `Survey`, and `Area`

---

### **Encounter Subtypes**

#### **1. AnimalEncounter**

_Records for encounters with individual animals (turtles, cetaceans, pinnipeds)_

**Extends with:**

- `taxon` (CharField): Taxonomic group (choices)
- `species` (CharField): Species classification
- `sex` (CharField): Male/female/unknown
- `maturity` (CharField): Adult/juvenile/hatchling
- `health` (CharField): Physical condition
- `activity` (CharField): Observed activity state
- `behaviour` (TextField): Condition/behaviour notes
- `habitat` (CharField): Environment type (beach position, in-water, etc.)
- `sighting_status` (CharField): Inferred tracking state (new/resighted/recapture)
- `sighting_status_reason` (TextField): Rationale for status
- `identifiers` (TextField): Space-separated list of all known ID tags
- `datetime_of_last_sighting` (DateTime): Last observation timestamp
- `site_of_last_sighting` (FK → Area): Last location

**Use Case:** Recording live animal sightings, stranding responses, tagging events

---

#### **2. TurtleNestEncounter**

_Records for turtle nest tracks and nests across their lifecycle_

**Extends with:**

- `nest_age` (CharField): Stage classification (false crawl, new, fresh, predated, hatched)
- `nest_type` (CharField): Type identifier (track only, track + nest, nest only)
- `species` (CharField): Turtle species
- `habitat` (CharField): Beach position
- `disturbance` (CharField): Evidence of predation/disturbance (yes/no/unknown)
- `nest_tagged` (CharField): Nest tag presence
- `logger_found` (CharField): Data logger deployment status
- `eggs_counted` (CharField): Nest excavation flag
- `hatchlings_measured` (CharField): Hatchling morphometric flag
- `fan_angles_measured` (CharField): Hatchling emergence track recordings

**Use Case:** Monitoring nesting beaches, tracking nest lifecycle, recording hatchling emergence

---

#### **3. LineTransectEncounter**

_Records for tally-based observations along a transect line_

**Extends with:**

- `transect` (LineStringField, WGS84): The traversed line geometry

**Related Observations:**

- `TrackTallyObservation`: Tally counts of turtle tracks
- `TurtleNestDisturbanceTallyObservation`: Tally counts of disturbed nests

**Use Case:** Saturation beach surveys, rapid track counts, high-pressure data collection where individual georeferencing is impractical

---

## Observation Model Hierarchy

### **Observation** (PolymorphicModel, base class)

_Base for all specific observation types recorded during an Encounter_

**Key Fields:**

- `encounter` (FK → Encounter, CASCADE): Required parent encounter
- `polymorphic_ctype` (inherited): Tracks concrete model type for API serialization

**Methods:**

- `observation_name`: Returns concrete model name (e.g., "TurtleMorphometricObservation")
- `can_change()`: Checks if editing is allowed based on parent Encounter QA status
- `latitude` / `longitude`: Delegates to encounter location

---

### **Observation Subtypes**

#### **1. MediaAttachment**

_File uploads (photos, videos, documents) associated with encounters_

**Fields:**

- `media_type`: Classification (photo/video/document)
- `attachment`: File storage reference
- Path pattern: `encounter/{source_id}/{filename}`

---

#### **2. TagObservation**

_Records flipper tags, PIT tags, satellite tags, genetic IDs, etc._

**Key Fields:**

- `tag_type` (CharField): Type (flipper-tag, pit-tag, satellite-tag, etc.)
- `tag_location` (CharField): Anatomical position (flipper, shoulder, carapace, etc.)
- `name` (CharField): Tag ID/serial number (db_indexed)
- `status` (CharField): Tag state (applied-new, resighted, applied-and-reading, etc.)
- `handler` (FK → User): Person handling tag
- `recorder` (FK → User): Person recording observation
- `comments` (TextField): Additional notes

**Use Cases:**

- Animal identification and recapture tracking
- Tagging success/failure documentation
- Tag lifecycle management

**Key Methods:**

- `encounter_history(tagname)`: All encounters associated with a tag
- `encounter_histories(tagname_list)`: Multiple tag encounter histories
- `is_new`: Boolean—first tag association
- `is_recapture`: Boolean—recapture status

---

#### **3. NestTagObservation**

_Turtle Nest Tags (TNTs)—composite IDs for nesting turtles_

**Components:**

- `flipper_tag_id`: Primary turtle identifier
- `date_nest_laid`: Nest creation calendar date
- `tag_label`: Optional additional label

---

#### **4. TurtleMorphometricObservation**

_Detailed size measurements of adult/juvenile turtles_

**Measured Fields (all with accuracy classifications):**

- `curved_carapace_length_mm` / `_min_mm`: Carapace length variants
- `straight_carapace_length_mm`: Alternative measurement
- `curved_carapace_width_mm`: Shell width
- `tail_length_*_mm`: Three variants (from carapace, vent, plastron)
- `plastron_length_mm`, `plastron_width_mm`
- `body_depth_mm`, `body_mass_g`
- And many more measurements...

**Accuracy Field:** Documents expected precision (±1mm, ±5mm, etc.)

---

#### **5. HatchlingMorphometricObservation**

_Size measurements of turtle hatchlings_

**Measured Fields:**

- `curved_carapace_length_mm`: Hatchling carapace length
- `straight_carapace_length_mm`: Alternative measurement
- `curved_carapace_width_mm`: Shell width
- `body_mass_g`: Weight
- Similar structure to TurtleMorphometricObservation but for hatchlings

---

#### **6. TurtleDamageObservation**

_Records of injuries, predation marks, and physical damage_

**Fields:**

- `damage_type` (FK → DamageCode): Classification
- `location` (CharField): Anatomical site
- `description` (TextField): Damage details
- `severity` (CharField): Assessment (minor/moderate/severe)

---

#### **7. TurtleNestObservation**

_Nest excavation results and contents documentation_

**Key Fields:**

- `eggs_counted` (IntegerField): Number of eggs
- `hatchlings_counted` (IntegerField): Number emerged
- `dead_in_shell` (IntegerField): Predated or non-viable
- `egg_status` (CharField): Classification
- `clutch_size_calculated` (IntegerField): Inferred from excavation

---

#### **8. TurtleNestDisturbanceObservation**

_Records of nest disturbance events and predation_

**Fields:**

- `disturbance_type` (CharField): Cause (predator type, human, natural)
- `disturbance_status` (CharField): Damage extent
- `comments` (TextField): Additional details

---

#### **9. TurtleHatchlingEmergenceObservation**

_Hatchling emergence events and emergence funnels_

**Key Fields:**

- `fan_angles` (JSONField): Recorded emergence track angles
- `emergence_type` (CharField): Emergence pattern

---

#### **10. TurtleTrackObservation**

_Track presence and characteristics_

**Fields:**

- `track_type` (CharField): Type classification
- `comments` (TextField): Track notes

---

#### **11. TurtleHatchlingEmergenceOutlierObservation**

_Exceptional emergence data points_

**Purpose:** Records data outside normal emergence patterns

---

#### **12. LoggerObservation**

_Data logger deployment and retrieval_

**Fields:**

- `logger_id` (CharField): Device identifier
- `logger_status` (CharField): Deployment state
- `comments` (TextField): Deployment notes

---

#### **13. TissueSampleObservation**

_Genetic or other tissue samples collected_

**Fields:**

- `sample_type` (CharField): Sample classification
- `storage_location` (CharField): Where stored
- `comments` (TextField): Sample notes

---

#### **14. ManagementAction**

_Actions taken during encounters (medications, repairs, releases)_

**Fields:**

- `action_type` (CharField): Classification
- `outcome` (CharField): Result status
- `comments` (TextField): Details

---

#### **15. LightSourceObservation**

_Artificial light sources at nesting beaches_

**Fields:**

- `light_source_type` (CharField): Type (street light, business sign, etc.)
- `brightness` (CharField): Intensity estimate
- `location_description` (TextField): Relative position

---

#### **16. TrackTallyObservation** _(for LineTransectEncounter)_

_Tally counts of turtle tracks along a transect_

**Fields:**

- `track_count` (IntegerField): Number observed
- `species` (CharField): Species classification

---

#### **17. TurtleNestDisturbanceTallyObservation** _(for LineTransectEncounter)_

_Tally counts of disturbed nests along a transect_

**Fields:**

- `disturbance_count` (IntegerField): Number observed
- `disturbance_type` (CharField): Cause classification

---

#### **18. DisturbanceObservation**

_General disturbance documentation_

**Fields:**

- `disturbance_type` (CharField): Classification
- `comments` (TextField): Details

---

## Supporting Models

### **Area** (Spatial boundary records)

**Types:**

- MPA (Marine Protected Area)
- Locality (Large geographical area)
- Site (Surveyed location)
- DBCA Region
- DBCA District

**Key Fields:**

- `area_type` (CharField): Classification
- `name` (CharField, unique per type)
- `geom` (PolygonField, WGS84): Boundary
- `centroid` (PointField): Cached centroid
- `northern_extent` (FloatField): Northernmost latitude
- `length_surveyed_m` / `length_survey_roundtrip_m`: Survey metrics
- `w2_location_code` / `w2_place_code`: WAMTRAM mapping

---

### **Campaign** (Coordinated observation efforts)

**Key Fields:**

- `destination` (FK → Area): Target locality
- `start_time` / `end_time` (DateTime): Campaign window
- `owner` (FK → Organisation): Responsible organization
- `team` (M2M → User): Participating staff
- `viewers` (M2M → Organisation): Data visibility permissions
- `comments` (TextField)

**Relationship:** Owns all Surveys and Encounters within its time/space bounds

---

### **Survey** (Individual field efforts)

**Key Fields:**

- `campaign` (FK → Campaign)
- `site` (FK → Area): Surveyed location
- `start_time` / `end_time` (DateTime): Survey window
- `start_user` / `end_user` (FK → User): Observers
- `comments` (TextField)
- `recorder` (FK → User)
- `reporter` (FK → User)
- `status` (FSMField): Same QA workflow as Encounter

**Related:** Many Encounters observed during a survey

---

### **SurveyEnd** (Survey completion records)

_Deprecated—kept for backward compatibility_

---

### **SurveyMediaAttachment** (Media for Surveys)

**Fields:**

- `survey` (FK → Survey)
- `attachment` (FileField): Media file
- Path pattern: `survey/{survey_id}/{filename}`

---

## Data Flow & Relationships

```
Campaign (high-level effort)
  └─ owns many Surveys
      └─ contains many Encounters
          ├─ AnimalEncounter
          ├─ TurtleNestEncounter
          └─ LineTransectEncounter
              └─ has many Observations (polymorphic)
                  ├─ MediaAttachment
                  ├─ TagObservation
                  ├─ TurtleMorphometricObservation
                  ├─ TurtleNestObservation
                  ├─ TrackTallyObservation
                  └─ [15 other subtypes...]

User (global actors)
  ├─ observed Encounters (as observer)
  ├─ reported Encounters (as reporter)
  ├─ handled TagObservations
  ├─ recorded TagObservations
  └─ [team membership, survey staffing, etc.]

Organisation
  ├─ owns Campaigns
  ├─ views shared Campaigns
  └─ [audit trail]

Area (spatial anchor)
  ├─ boundaries for Campaigns (destination)
  ├─ locality for Encounters (area)
  ├─ surveyed site for Encounters (site)
  └─ [hierarchical/administrative regions]
```

---

## QA/Curation Workflow

**Encounter Status Progression** (django-fsm):

1. **new**: Initial state after creation
2. **imported**: Bulk import completed
3. **manual_input**: Manually entered data
4. **proofread**: Human verification complete
5. **curated**: Final data review approved
6. **published**: Released for analysis/sharing
7. **flagged** _(side state)_: Requires attention
8. **rejected** _(side state)_: Discarded/erroneous

**Observation Editability:**

- Observations can only be edited if parent Encounter is in: new, imported, manual_input, or flagged
- Prevents accidental modification of curated records

**Audit Trail:**

- State changes logged via django-fsm-log (`StateLog`)
- Preserves data lineage and change history

---

## Key Technical Features

### **Polymorphic Inheritance**

- Uses `django-polymorphic` for single-table inheritance pattern
- Reduces DB table bloat while enabling type-specific behavior
- Serializers detect `polymorphic_ctype` for API responses

### **Spatial Queries (PostGIS)**

- All locations stored in WGS84 (SRID 4326)
- Supports point-in-polygon queries (`geom__coveredby`)
- LineString for transect paths
- Polygon boundaries for Areas
- Enables map visualization, GIS analysis, proximity queries

### **Legacy Source Tracking** (`LegacySourceMixin`)

- `source` + `source_id` unique constraint prevents duplicates on re-import
- Batch imports can safely re-run if idempotent
- Paper record IDs follow pattern: `<prefix><date><running-number>`

### **Quality Control** (`QualityControlMixin`)

- FSM-enforced state workflow
- Audit logging of transitions
- Prevents data modification after curation

### **Timezone Handling**

- All timestamps stored in UTC
- Displayed/entered in local timezone (configured in settings.TZ)
- Consistent across web interface and API

---

## API & Serialization

**DRF Integration:**

- Serializers in `observations/serializers.py` and `observations/api.py`
- Viewsets mounted at `/api/1/` via `wastd/router.py`
- Polymorphic serializers detect model type via `polymorphic_ctype`
- Standard CRUD operations + custom actions (state transitions, bulk operations)

---

## Common Queries

### **Find all encounters with a specific tag:**

```python
tag_obs = TagObservation.objects.filter(name="ABC123")
encounters = set(t.encounter for t in tag_obs)
```

### **Get animals by sighting status:**

```python
recent_animals = AnimalEncounter.objects.filter(
    sighting_status__in=["new", "resighted"]
)
```

### **Survey completion stats:**

```python
survey = Survey.objects.get(pk=123)
stats = {
    "encounters": survey.encounter_set.count(),
    "animals": survey.encounter_set.filter(
        polymorphic_ctype__model="animalencounter"
    ).count(),
    "nests": survey.encounter_set.filter(
        polymorphic_ctype__model="turtlenestencounter"
    ).count(),
}
```

### **Nest lifecycle over time:**

```python
nests = TurtleNestEncounter.objects.filter(
    site__name="Exmouth Beach"
).order_by("when")
```

---

## Summary

The observations schema implements a **flexible, spatially-aware event-observation model** suitable for:

- ✅ Opportunistic wildlife encounters
- ✅ Systematic surveys with strict protocols
- ✅ Rapid data collection (tallies, photos)
- ✅ Multi-site, multi-user, multi-organization coordination
- ✅ Legacy data migration (WAMTRAM)
- ✅ Rigorous data quality workflows
- ✅ Advanced spatial analysis

The hierarchical design (Encounter → Observation subtypes) balances **flexibility** (easily add new observation types) with **structure** (enforce domain-specific fields), making it maintainable and extensible.
