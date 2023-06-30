"""Utilities and functions related to ODK.
"""
from django.conf import settings
from django.contrib.gis.geos import Point
import requests
import xmltodict

ODK_API_URL = settings.ODK_API_URL


def get_auth_headers(email=None, password=None):
    """Returns a dict containing authorization headers for ODK.
    """
    if not email:
        email = settings.ODK_API_EMAIL
    if not password:
        password = settings.ODK_API_PASSWORD

    headers = {"Content-Type": "application/json"}
    data = {
        "email": email,
        "password": password,
    }
    resp = requests.post(f"{ODK_API_URL}/sessions", headers=headers, json=data)
    resp.raise_for_status()
    token = resp.json()["token"]
    headers["Authorization"] = f"Bearer {token}"

    return headers


def get_projects(auth_headers):
    """Returns all projects, with nested forms.
    """
    resp = requests.get(f"{ODK_API_URL}/projects?forms=true", headers=auth_headers)
    resp.raise_for_status()

    return resp.json()


def get_form(auth_headers, project_id, form_id,):
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}", headers=auth_headers)
    resp.raise_for_status()

    return resp.json()


def get_submissions(auth_headers, project_id, form_id, form_version):
    """Returns all submissions to an ODK form, as JSON.
    """
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}/submissions", headers=auth_headers)
    resp.raise_for_status()

    return resp.json()


def get_submission(auth_headers, project_id, form_id, instance_id):
    """Returns data for a single submission, parsed as a dict.
    """
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}/submissions/{instance_id}.xml", headers=auth_headers)
    resp.raise_for_status()
    data = xmltodict.parse(resp.content, xml_attribs=False)['data']

    return data


def get_form_submission_data(auth_headers, project_id, form_id, form_version=None):
    """Returns all data for a form
    """
    # If form_version is None, find the current form version.
    if not form_version:
        # Use the current form version.
        form = get_form(auth_headers, project_id, form_id)
        form_version = form["version"]

    # Get submissions for the form.
    submissions = get_submissions(auth_headers, project_id, form_id, form_version)

    # Get all individual submission data.
    submission_data = []
    for submission in submissions:
        submission_data.append(get_submission(auth_headers, project_id, form_id, submission["instanceId"]))

    return submission_data


def parse_geopoint(geopoint):
    """Parse an ODK geopoint, which will be represented as a string in the format 'latitude longitude altitude accuracy'.
    Returns a Django Point geometry object in WGS84.
    Example: '-31.7989645 115.8046184 -7.700000286102295 4.835'
    Reference: https://docs.getodk.org/form-question-types/#location-widgets
    """
    geopoint = [float(g) for g in geopoint.split()]
    return Point(geopoint[1], geopoint[0], srid=4326)
