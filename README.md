# Western Australian Sea Turtles Database (WASTD)

This project is the Department of Biodiversity, Conservation and Attractions
Sea Turtles Database corporate application.

# Project layout / description

- `wastd`: the core Django project directory, containing common settings, configuration and templates.
- `observations`: the primary data model for the project, defining the `Encounter` and `Observation` models and subclasses.
- `users`: an extension of the Django `contrib.auth.models.User` class, customised for this project.
- `wamtram`: auto-generated model classes to provide readonly ORM utility for the legacy WAMTRAM database.
- `tagging`: an "interim" application to save data from the WAMTRAM database locally, prior to a future refactor of that data model into the `observations` application.

The intent is for this project to replace the WAMTRAM legacy project and to act as the repository for
turtle tagging data. The `wamtram` application was created to ease access to the legacy database, and
the `tagging` application was created as an interim step to refactoring the legacy data into the
Encounter/Observation model defined in the `observations` application. It is expected that `wamtram` will
be removed after data migration, and that `tagging` will be removed after the data is refactored.

# Installation

The recommended way to set up this project for development is using
[Poetry](https://python-poetry.org/docs/) to install and manage a virtual Python
environment. With Poetry installed, change into the project directory and run:

    poetry install

To run Python commands in the virtualenv, thereafter run them like so:

    poetry run python manage.py

Manage new or updating project dependencies with Poetry also, like so:

    poetry add newpackage==1.0

# Environment variables

This project uses **python-dotenv** to set environment variables (in a `.env` file).
The following variables are required for the project to run:

    DATABASE_URL="postgis://USER:PASSWORD@HOST:5432/DATABASE_NAME"

Variables below may also need to be defined (context-dependent):

    SECRET_KEY="ThisIsASecretKey"
    DEBUG=True

# Running

Use `runserver` to run a local copy of the application:

    poetry run python manage.py runserver 0:8080

Run console commands manually:

    poetry run python manage.py shell_plus

# Media uploads

The production system stores media uploads in Azure blob storage.
Credentials for doing so should be defined in the following environment
variables:

    AZURE_ACCOUNT_NAME=name
    AZURE_ACCOUNT_KEY=key
    AZURE_CONTAINER=container_name

To bypass this and use local media storage (for development, etc.) simply set
the `LOCAL_MEDIA_STORAGE=True` environment variable and create a writable
`media` directory in the project directory.

# Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/wastd .

# Docs

Use `sphinx-build` build docs locally:

    poetry run sphinx-build -b html docs _build

Use `http.server` serve them:

    poetry run python -m http.server --directory _build 8080

# Pre-commit hooks

This project includes the following pre-commit hooks:

- TruffleHog (credential scanning): https://github.com/marketplace/actions/trufflehog-oss

Pre-commit hooks may have additional system dependencies to run. Optionally
install pre-commit hooks locally like so:

    poetry run pre-commit install

Reference: https://pre-commit.com/
