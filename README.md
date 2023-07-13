# Western Australian Sea Turtles Database (WASTD)

This project is the Department of Biodiversity, Conservation and Attractions
Sea Turtles Database corporate application.

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

This project uses **django-confy** to set environment variables (in a `.env` file).
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

# Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/wastd .

# Docs

To build docs locally:

    poetry run sphinx-build -b html docs _build

To serve them:

    poetry run python -m http.server --directory _build 8080
