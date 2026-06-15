# ODK Cloud Data Import Summary

## Overview
The `observations/odk.py` module provides utility functions to import turtle and marine wildlife survey data from ODK (Open Data Kit) Cloud submissions. The module contains **7 main import functions** plus 2 helper functions for user management.

---

## Helper Functions

### `create_new_user(name)`
**Purpose:** Creates and returns a new User object based on a name value.
- Converts name to a unique lowercase username with underscores
- Appends underscores to guarantee uniqueness
- Sets password as unusable
- **Used by:** All import functions

### `get_user(reporter)`
**Purpose:** Matches a reporter name to an existing active user, or creates a new one.
- Returns "Unknown user" if no reporter name is provided
- Logs info/warning messages for debugging
- **Used by:** All import functions

---

## Main Import Functions

### 1. `import_turtle_track_or_nest(form_id="turtle_track_or_nest")`

**Purpose:** Import comprehensive turtle track/nest encounter data from the full ODK form.

**Creates:**
- 1 `TurtleNestEncounter` (covers nest, track, or combined encounters)
- 0–1 `TurtleNestObservation` (egg count and excavation details)
- 0–1 `TurtleTrackObservation` (unidentified species track measurements)
- 0–1 `NestTagObservation` (nest tags seen/deployed with dates)
- 0–1 `TurtleHatchlingEmergenceObservation` (fan angles, hatchling emergence timing)
- 0+ `TurtleNestDisturbanceObservation` (multiple disturbance/predation events)
- 0+ `LoggerObservation` (temperature/humidity loggers deployed)
- 0+ `HatchlingMorphometricObservation` (hatchling body measurements)
- 0+ `TurtleHatchlingEmergenceOutlierObservation` (outlier track measurements)
- 0+ `LightSourceObservation` (light source data measured in fan angles)
- Multiple `MediaAttachment` records for nest, eggs, tracks, tags, loggers, disturbances, and outliers

**Data Collected:**
- **Core encounter:** location (geopoint), timestamp, observer, nest age, nest type, species, habitat
- **Nest details:** egg counts (shells, live/dead hatchlings, undeveloped/unhatched eggs), nest depth
- **Track measurements:** front/rear track width, carapace drag width, step length, tail pokes
- **Hatchling emergence:** bearing angles (water, leftmost, rightmost tracks), track counts, emergence time
- **Disturbance:** cause, confidence level, severity for multiple events
- **Loggers:** logger type, deployment status, logger ID
- **Light sources:** bearing, type, description for multiple sources
- **Photos:** up to 3 nest photos, egg photos, track photos, tag photos, disturbance photos, logger photos, outlier photos, light source photos

---

### 2. `import_turtle_track_or_nest_simple(form_id="beach_tracks_nest_simple")`

**Purpose:** Import simplified/quick-entry turtle track/nest data (fewer details than full form).

**Creates:**
- 1 `TurtleNestEncounter` (simplified)
- 0–1 `TurtleTrackObservation` (minimal track data)
- 0+ `TurtleNestDisturbanceObservation` (disturbance events)
- Multiple `MediaAttachment` records (track photos)

**Data Collected:**
- **Core encounter:** location, timestamp, nest type, species, habitat, observer
- **Track measurements:** max track width (front only), tail pokes
- **Disturbance:** space-delimited list of disturbance causes (e.g., "fox cat dog")
- **Photos:** up to 2 track photos

---

### 3. `import_site_visit_start(form_id="site_visit_start", initial_duration_hr=8)`

**Purpose:** Create a new `Survey` record from a site visit start form submission.

**Creates:**
- 1 `Survey` object (with estimated end time set to initial_duration_hr offset)
- Team members linked via M2M relationship
- 1 `SurveyMediaAttachment` (site conditions photo)

**Data Collected:**
- **Survey metadata:** start location (geopoint), accuracy, start time, device ID, production status
- **Team assignment:** comma-separated list of team member names (matched or created as new users)
- **Site matching:** auto-guesses area and site based on start location
- **Training flag:** surveys at training/testing sites marked as non-production
- **Photo:** site conditions photo at start

---

### 4. `import_site_visit_end(form_id="site_visit_end", duration_hr=8)`

**Purpose:** Update an existing `Survey` record by matching and linking site visit end data.

**Modifies:**
- Existing `Survey` object (matches by site and time window)

**Data Updated:**
- End location (geopoint), accuracy, end time
- End comments
- End source ID (form instance ID)
- 1 `SurveyMediaAttachment` (site conditions photo at end)

**Matching Algorithm:**
- Finds site based on end location (coverage polygon)
- Locates `Survey` within site that started within `duration_hr` hours before end time
- Updates if exactly one match found; warns if zero or multiple matches

---

### 5. `import_marine_wildlife_incident(form_id="marine_wildlife_incident")`

**Purpose:** Import marine wildlife incident/interaction data (typically injured/sick animals).

**Creates:**
- 1 `AnimalEncounter` (marine animal observation)
- 0–1 `TurtleMorphometricObservation` (body measurements if provided)
- 0+ `TurtleDamageObservation` (injury/damage records)
- 0+ `TagObservation` (flipper/PIT tag data if scanned)
- Multiple `MediaAttachment` records (habitat, carapace, head, scene photos)

**Data Collected:**
- **Animal details:** taxon, species, sex, maturity, habitat
- **Health status:** health status, activity, behaviour, cause of death (if deceased), death cause confidence
- **Observation checks:** checked for injuries, scanned for PIT tags, checked for flipper tags
- **Morphometrics:** curved carapace length/width, tail length, head width (with accuracy ratings)
- **Damage records:** damage type, severity (multiple records possible)
- **Tags:** flipper tag IDs, PIT tag data (multiple records possible)
- **Photos:** habitat photo (1), carapace photo, head photos (top, side, front), habitat scene photos (2)

---

### 6. `import_turtle_sighting(form_id="turtle_sighting")`

**Purpose:** Import simple turtle sighting observations (non-incident encounters).

**Creates:**
- 1 `AnimalEncounter` (turtle sighting)

**Data Collected:**
- **Sighting details:** location (geopoint), observation time, species, maturity, comments
- **Behavior:** interaction type (mapped to behavior field)
- **Classification:** always set as taxon "Cheloniidae", encounter type "other"

---

### 7. `import_predator_or_disturbance(form_id="predator_or_disturbance")`

**Purpose:** Import standalone predator or disturbance observations (not tied to a specific nest/encounter).

**Creates:**
- 1 `Encounter` (disturbance type)
- 1+ `DisturbanceObservation` (predator/disturbance event details)
- 1 `MediaAttachment` (disturbance/predator photo)

**Data Collected:**
- **Event details:** location (geopoint), timestamp, observer/reporter
- **Disturbance info:** cause, confidence level, comments
- **Photo:** disturbance/predator identification photo
- **Site matching:** auto-guesses area and site based on location

---

## Common Data Fields Across All Imports

### User/Reporter Data
- Reporter name → matched to User or new User created
- Observer assigned to reporter
- Device ID recorded in comments (when available)

### Spatial/Temporal Data
- **Location:** Geopoint (WGS84 SRID 4326) parsed from ODK submission
- **Timestamp:** ISO 8601 format, with fallback logic for old vs. new form versions
- **Accuracy:** Geopoint accuracy in meters (where available)

### Source Tracking
- `source = "odk"` (OpenDataKit)
- `source_id = instanceID` (unique form instance identifier from ODK)
- `status = "imported"` (initial QA/curation status)

### Media Attachments
- Source: `SOURCE_DIGITAL_CAPTURE_ODK`
- Media type: `"photograph"` (all current imports handle photos)
- Attachments downloaded directly from ODK Cloud API

### Deduplication
- All import functions check for existing records by `(source="odk", source_id=instanceID)` to prevent re-importing

---

## Error Handling

- Each submission wrapped in try/except block
- Exceptions logged with full traceback via `LOGGER.exception()`
- Import continues with next submission on error (partial import on failure)
- Missing optional fields handled gracefully with None/NA_VALUE defaults

---

## Authentication

- All functions accept optional `auth_headers` parameter (pre-computed headers optional)
- If not provided, headers fetched via `get_auth_headers()`
- Project ID retrieved from `settings.ODK_API_PROJECTID`

---

## Related Imports

The module depends on helper functions from `wastd.odk`:
- `get_auth_headers()` – Authenticate with ODK Cloud API
- `get_form_submission_data()` – Retrieve form submissions
- `parse_geopoint()` – Parse ODK geopoint format
- `parse_geopoint_accuracy()` – Extract accuracy from geopoint
- `get_submission_attachment()` – Download media files

---

## Summary: Data Types Importable from ODK

| Data Type | Form(s) | Quantity | Notes |
|-----------|---------|----------|-------|
| Turtle Nests | `turtle_track_or_nest` | 1 per submission | Full detail level |
| Turtle Tracks | `turtle_track_or_nest`, `beach_tracks_nest_simple` | 0–1 per encounter | Includes width, step, tail measurements |
| Turtle Sightings | `turtle_sighting` | 1 per submission | Simple observation |
| Marine Wildlife Incidents | `marine_wildlife_incident` | 1 per submission | Injured/sick animal details |
| Predator/Disturbance Events | `predator_or_disturbance` | 1+ per submission | Can have multiple disturbance obs |
| Nest Disturbances | `turtle_track_or_nest` | 0+ per nest | Multiple events per nest |
| Hatchling Measurements | `turtle_track_or_nest` | 0+ per nest | Individual hatchling morphometrics |
| Track Outliers | `turtle_track_or_nest` | 0+ per nest | Track count/bearing data |
| Light Sources | `turtle_track_or_nest` | 0+ per nest | Bearing and type |
| Temperature Loggers | `turtle_track_or_nest` | 0+ per nest | Logger deployment status |
| Nest Tags | `turtle_track_or_nest` | 0–1 per nest | Flipper tag/label data |
| Site Visits | `site_visit_start`, `site_visit_end` | 1 per visit pair | Start/end location and team |
| Photographs | All forms | Multiple per submission | Automatically downloaded and linked |
| User/Team Data | All forms | Variable | Reporters and team members created as needed |
