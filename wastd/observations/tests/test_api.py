from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()

# Create an AnimalEncounter from MWI 0.6 data
# Create a TurtleNestEncounter from Track or Nest 1.0 (with TNdist, HatchlingEm, HEoutlier, LightSource, TurtleNestEnc eggs, HatchlingMorph)
# Pred or Dist > Enc with Distobs
# SVE > SiteVisitEnd
# SVS > Survey

# TSC: AreaEncounter (Taxon/CommunityAE) > ObsGroup (polymorphic)
# enc = AreaEncounter.objects.last() # for source and source_id
# {'source': 10, 'source_id': '94654', 'sample_type': 'blood-sample', 'sample_destination': '', 'sample_label': '[]', 'obstype': 'PhysicalSample'}
# Get Auth token from profile
# curl  -H 'Authorization: Token XXX' -d
# "format=json&source=10&source_id=85464&permit_type=kermit&sample_type=blood-sample&sample_destination=department&sample_label=test&obstype=PhysicalSample"
# http://localhost:8220/api/1/occ-observation/

# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8220/api/1/occ-observation/?format=json" -d
# "obstype=AssociatedSpecies&source=10&source_id=85464&taxon=26599"

# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8220/api/1/occ-observation/?format=json" -d
# "obstype=AssociatedSpecies&source=10&source_id=85464&taxon=26599"

# M2M:
# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8211/api/1/occ-observation/?format=json" -d
# "obstype=AnimalObservation&source=10&source_id=85464&secondary_signs=7&secondary_signs=13"

# File attachments:
# curl -X POST -H "Authorization: Token XXX"
# "http://localhost:8211/api/1/occ-observation/?format=json" -F
# "obstype=FileAttachment" -F "source=10" -F "source_id=85464" -F
# "attachment=@/path/to/file"

# Test that occ-observation request parameter filter obsgroup works
# Create three separate ObsGroup models, e.g. one each of PhysicalSample, AssociatedSpecies, AnimalObservation.
# Test /api/1/occ-observation/ returns all three existing ObsGroup models
# Test /api/1/occ-observation/?obstype=AssociatedSpecies returns only obstype AssociatedSpecies - repeat for other two ObsGroup models

# Test that ObsGroup Serializers allow empty/missing/NA in R = None in Python non-required fields
# e.g. permit_type is NA in R, arrives as None in Python
# {'source': 10, 'source_id': '4', 'sample_type': 'frozen-carcass', 'sample_destination': 'wa-museum', 'sample_label': '[WA Museum]kmd091', 'permit_type': None, 'obstype': 'PhysicalSample'}
# After adding "required=False" to serializer fields, we can omit a field, e.g. the following request has no permit_type
# [INFO] [API][ObservationGroupPolymorphicSerializer] called with data {'source': 10, 'source_id': '4', 'sample_type': 'frozen-carcass', 'sample_destination': 'wa-museum', 'sample_label': '[WA Museum]kmd091', 'obstype': 'PhysicalSample'}
# [INFO] <class 'occurrence.models.PhysicalSample'>Serializer.create after enc with data {'sample_type': <SampleType: Frozen carcass>, 'sample_destination': <SampleDestination: WA Museum>, 'sample_label': '[WA Museum]kmd091', 'encounter': <TaxonAreaEncounter: Encounter of [24098][PHACAL] (Species) Phascogale calura (Gould) at [Fauna Site] (south-glencoe) South Glencoe on 1991-07-11 16:00:00+00:00 by TSC Admin>}
# [INFO] "POST /api/1/occ-observation/ HTTP/1.1" 201 4214


# TurtleNestEncounter sample data (test POST)
# [{"source": "odk",
#   "source_id": "uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb",
#   "reporter": 4,
#   "observer": 4,
#   "comments": "Device ID 2856338745efba86",
#   "where": "POINT (114.052963333333 -21.8359983333333)",
#   "location_accuracy": 10,
#   "when": "2020-02-22 22:36:26",
#   "nest_age": "fresh",
#   "nest_type": "false-crawl",
#   "species": "chelonia-mydas"}]

# Florian to add expected test data for Ash


class ObservationSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # TODO: test user/group permissions properly
        self.user = User.objects.create_superuser('testuser', 'testuser@test.com', 'pass')
        self.client.login(username='testuser', password='pass')

    def test_get_list_endpoints(self):
        url = reverse('api:encounter-list')
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        url = reverse('api:turtlenestencounter-list')
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, 200)

    def test_post_encounter(self):
        """Test the POST endpoint for Encounter
        """
        url = reverse('api:encounter-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': "uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb",
                "where": "POINT (114.0 -21.0)",
                "when": "2020-01-01 12:00:00",
                "reporter": self.user.pk,
                "observer": self.user.pk,
            }
        )
        self.assertEqual(resp.status_code, 201)

    def test_post_turtlenestencounter(self):
        """Test the POST endpoint for TurtleNestEncounter
        """
        url = reverse('api:turtlenestencounter-list')
        resp = self.client.post(
            url,
            {
                'source': 'odk',
                'source_id': "uuid:673f1150-4d60-4cc5-846a-ebca5a98d4eb",
                "where": "POINT (114.0 -21.0)",
                "when": "2020-01-01 12:00:00",
                "reporter": self.user.pk,
                "observer": self.user.pk,
                "nest_age": "fresh",
                "nest_type": "false-crawl",
                "species": "chelonia-mydas",
            }
        )
        self.assertEqual(resp.status_code, 201)
