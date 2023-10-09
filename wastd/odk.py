"""Utilities and functions related to ODK.
"""
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.files import File
import requests
import xmltodict
from tempfile import TemporaryFile
import logging

from observations.models import Encounter


ODK_API_URL = settings.ODK_API_URL
logger = logging.getLogger('turtles')

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


def get_submissions_metadata(auth_headers, project_id, form_id):
    """Returns metadata about all submissions to an ODK form, as a dict.
    """
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}/submissions", headers=auth_headers)
    resp.raise_for_status()
    return resp.json()


def get_submission(auth_headers, project_id, form_id, instance_id):
    """Returns data for a single submission, parsed as a dict.
    """
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}/submissions/{instance_id}.xml", headers=auth_headers)
    resp.raise_for_status()
    
    try:
        data = xmltodict.parse(resp.content, xml_attribs=False)['data']
    except Exception as e:
        print(str(e)) # print the exception message
        return []
    
    return data


def get_form_submission_data(auth_headers, project_id, form_id, skip_existing=True, skip_rejected=True):
    """Returns submission data for an ODK form, as JSON.
    Skips records that have already been imported by default.
    Skips records that are in "rejected" state in ODK, by default.
    """
    # Get submission metadata for the form.
    submissions_metadata = get_submissions_metadata(auth_headers, project_id, form_id)
    
    # Get individual submission data records.
    submission_data = []
    for metadata in submissions_metadata:
        if skip_existing:  # Check to see if record is already present in the local database.
            if Encounter.objects.filter(source='odk', source_id=metadata["instanceId"]).exists():
                continue
        
        if skip_rejected and metadata["reviewState"] == "rejected":
            logger.info("skipping rejected: " + metadata["instanceId"])
            continue
        
        submission = get_submission(auth_headers, project_id, form_id, metadata["instanceId"])
        submission_data.append(submission)

    return submission_data


def parse_geopoint(geopoint):
    """Parse an ODK geopoint, which will be represented as a string in the format 'latitude longitude altitude accuracy'.
    Returns a Django Point geometry object in WGS84.
    Example: '-31.7989645 115.8046184 -7.700000286102295 4.835'
    Reference: https://docs.getodk.org/form-question-types/#location-widgets
    """
    geopoint = [float(g) for g in geopoint.split()]
    return Point(geopoint[1], geopoint[0], srid=4326)


def parse_geopoint_accuracy(geopoint):
    """Parse an ODK geopoint, which will be represented as a string in the format 'latitude longitude altitude accuracy'.
    Returns the final element as a float, which is the accuracy.
    """
    geopoint = [float(g) for g in geopoint.split()]
    return geopoint[-1]


def get_submission_attachment(auth_headers, project_id, form_id, instance_id, filename):
    """Download a single attachment for a given form submission and return it as a Django File object.
    Reference: https://odkcentral.docs.apiary.io/#reference/submissions/attachments/downloading-an-attachment
    """
    resp = requests.get(f"{ODK_API_URL}/projects/{project_id}/forms/{form_id}/submissions/{instance_id}/attachments/{filename}", headers=auth_headers)
    resp.raise_for_status()

    # Response will be the attachment body.
    tempfile = TemporaryFile()
    tempfile.write(resp.content)  # Turn the downloaded content into a Python file.
    file = File(tempfile, name=filename)  # Pass that to a Django File.

    return file
