# WAStD – GitHub Copilot Instructions

## Project overview

**WAStD** (Western Australian Sea Turtles Database) is a Django 5.2 web application maintained by the Department of Biodiversity, Conservation and Attractions (DBCA, WA). It records turtle and marine mammal encounter data, replacing the legacy WAMTRAM system, and exposes a REST API alongside a curation-focused front end.

- Version: see `pyproject.toml` → `project.version`
- Python ≥ 3.13, managed with [uv](https://docs.astral.sh/uv/)
- Database: PostgreSQL + PostGIS (`postgis://…`)
- Linter: **ruff** (line length 140, excludes `migrations/`)

## Environment setup

**Always activate the virtualenv before running any Python command:**

```bash
source .venv/bin/activate
```

Then use `python manage.py …` as normal. Alternatively, prefix commands with `uv run`:

```bash
uv run python manage.py migrate
```

Install/sync dependencies:

```bash
uv sync
```

Add a new dependency:

```bash
uv add somepackage==1.2.3
```

## Project layout

```
wastd/                   # Core Django project package
├── settings.py          # Main settings (env-driven via python-dotenv)
├── test-settings.py     # Test-only settings overrides
├── urls.py              # Root URL configuration
├── router.py            # DRF router (API)
├── context_processors.py
├── middleware.py
└── templates/           # Base templates

observations/            # PRIMARY app — core data model
├── models.py            # Encounter, Observation and all subclasses
├── views.py             # Class-based views
├── urls.py              # URL patterns (namespace: observations)
├── admin.py             # Grappelli-based admin
├── api.py               # DRF serializers / viewsets
├── serializers.py
├── filters.py           # django-filter FilterSets
├── resources.py         # django-import-export resources
├── signals.py           # Django signals (pre/post save)
├── lookups.py           # Choice tuples and constants
├── forms.py
├── utils.py
├── odk.py               # ODK data ingestion helpers
├── templatetags/        # Custom template tags
├── templates/           # App-level templates
├── migrations/
├── fixtures/
└── tests/               # Unit tests (test_api.py, test_views.py, …)

users/                   # Custom User model (extends AbstractUser)
├── models.py            # User, Organisation
├── views.py
├── urls.py
└── templates/

marine_mammal_incidents/ # Marine mammal incident recording app
├── models.py
├── views.py
├── urls.py
└── templates/

wamtram2/                # Read-only ORM bridge to the legacy WAMTRAM MSSQL DB
├── models.py            # Auto-generated models
├── routers.py           # Database router (routes wamtram2 app to mssql DB)
└── templates/

kustomize/               # Kubernetes deployment manifests
docs/                    # Project documentation
staticfiles/             # Collected static files (do not edit)
media/                   # Local media uploads (dev only)
```

## Key conventions

### Models

- **`Encounter`** (in `observations/models.py`) is the central `PolymorphicModel`. Subclasses: `AnimalEncounter`, `TurtleNestEncounter`, `LineTransectEncounter`.
- **`Observation`** is also a `PolymorphicModel` with many subclasses (e.g. `TurtleNestObservation`, `TagObservation`, `HatchlingMorphometricObservation`). Each links to an `Encounter` via FK.
- QA/curation status is managed via **django-fsm** transitions: `new → imported → manual_input → proofread → curated → published`, plus `flagged` and `rejected` side states.
- `source` + `source_id` is a `unique_together` constraint on `Encounter`. The `source_id` is auto-set in the `encounter_pre_save` signal from `instance.short_name` if empty — but only after the instance has a PK (guard with `instance.pk` before accessing reverse FK relations in signals).
- Spatial fields use `django.contrib.gis` (PostGIS). Point fields are WGS84 (SRID 4326).

### URLs / namespaces

| App                     | Namespace                 | Example name                    |
| ----------------------- | ------------------------- | ------------------------------- |
| observations            | `observations`            | `observations:encounter-detail` |
| users                   | `users`                   | `users:user-detail`             |
| marine_mammal_incidents | `marine_mammal_incidents` | `marine_mammal_incidents:…`     |
| API (DRF)               | `api`                     | `api:…`                         |

### Views

- Class-based views using Django's generic CBVs plus `DetailViewBreadcrumbMixin` / `ListViewBreadcrumbMixin` from `dbca-utils`.
- List views use `django-filter` `FilterSet` classes and `ResourceDownloadMixin` for CSV/XLSX export.
- Authentication: most views are public read; write/curate operations require `is_staff`.

### API

- Django REST Framework, routed via `wastd/router.py`, mounted at `/api/1/`.
- Serializers and viewsets live in `observations/api.py` and `observations/serializers.py`.

### Templates

- Base template: `wastd/templates/base_wastd.html` (extends `webtemplate-dbca`).
- App templates live in `<app>/templates/<app>/`.
- Template tags: `observations/templatetags/observations.py`.

### Admin

- Uses **Grappelli** skin + **nested-admin** for inline observations.
- Custom dashboard in `wastd/dashboard.py`.

### Settings

- All secrets and connection strings come from environment variables (`.env` file via `python-dotenv`).
- Required: `DATABASE_URL` (PostGIS connection string).
- Optional: `SECRET_KEY`, `DEBUG`, `LOCAL_MEDIA_STORAGE`, `AZURE_*` (blob storage), `SENTRY_DSN`.
- Test settings: `wastd/test-settings.py` — use `--settings wastd.test-settings` when running tests.

### Testing

Run the full test suite (requires a live PostGIS database):

```bash
python manage.py test --noinput --failfast --settings wastd.test-settings
```

Tests live in `<app>/tests/` (package) or `<app>/tests.py`. Do **not** run tests in parallel — setUp methods may violate DB constraints when concurrent.

### Linting

```bash
ruff check .
ruff format .
```

Ruff is configured in `pyproject.toml`: line length 140, auto-fix enabled, `migrations/` excluded.

### Dependencies

Managed with `uv`. Do not edit `uv.lock` by hand. To add/remove packages:

```bash
uv add somepackage==1.2.3
uv remove oldpackage
uv sync
```

### Migrations

Generate and apply migrations with the activated virtualenv:

```bash
python manage.py makemigrations
python manage.py migrate
```

Never edit migration files by hand unless resolving a genuine conflict.
