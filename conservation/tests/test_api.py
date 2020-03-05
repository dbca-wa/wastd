from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from taxonomy.models import Community, Taxon
from conservation.models import (
    FileAttachment,
    ConservationList,
    ConservationCategory,
    CommunityConservationListing,
    ConservationCriterion,
    Document,
    TaxonConservationListing,
)

# Test updating taxon-conservationlisting with none, one, many cat and crit
# Test updating community-conservationlisting


User = get_user_model()


class ObservationGroupSerializerTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'testuser@test.com', 'pass')
        self.user.is_staff = True
        self.user.is_superuser = True  # TODO: test user/group permissions properly
        self.user.save()
        self.client.login(username='testuser', password='pass')
        self.community = Community.objects.create(code='Test community')
        self.taxon = Taxon.objects.create(name_id=0, name='Test taxon')
        self.clist = ConservationList.objects.create(code='test-list', label='Test conservation list')
        self.ccategory = ConservationCategory.objects.create(
            conservation_list=self.clist, code='test-category', label='Test conservation category')
        self.ccriterion = ConservationCriterion.objects.create(
            conservation_list=self.clist, code='test-criterion')
        self.taxon_listing = TaxonConservationListing.objects.create(taxon=self.taxon)
        self.document = Document.objects.create(title='Test document')
        f = SimpleUploadedFile('file.txt', b'file_content')
        self.fileattachment = FileAttachment.objects.create(
            attachment=f,
            content_type=ContentType.objects.get_for_model(Document),
            object_id=self.document.pk
        )
        self.ccl = CommunityConservationListing.objects.create(community=self.community)

    def test_get_endpoints(self):
        for i in [
            'conservationlist',
            'conservationcategory',
            'conservationcriterion',
            'taxonconservationlisting',
            'communityconservationlisting',
        ]:
            url = reverse('conservation_api:{}-list'.format(i))
            resp = self.client.get(url, {'format': 'json'})
            self.assertEqual(resp.status_code, 200)
