from django.test import RequestFactory
from test_plus.test import TestCase
from .factories import UserFactory, AreaFactory
from users.views import (
    UserRedirectView,
    UserUpdateView,
    transfer_user,
    change_user_for_area,
)


class BaseUserTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.area = AreaFactory()
        self.factory = RequestFactory()


class TestUserRedirectView(BaseUserTestCase):
    def test_get_redirect_url(self):
        # Instantiate the view directly. Never do this outside a test!
        view = UserRedirectView()
        # Generate a fake request
        request = self.factory.get("/fake-url")
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        view.request = request
        # Expect: '/users/<pk>/'
        self.assertEqual(view.get_redirect_url(), "/users/{0}/".format(self.user.pk))


class TestUserUpdateView(BaseUserTestCase):
    def setUp(self):
        """Set up."""
        # call BaseUserTestCase.setUp()
        super(TestUserUpdateView, self).setUp()
        # Instantiate the view directly. Never do this outside a test!
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get("/fake-url")
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        self.view.request = request
        # TODO add Encounters, reconstruct missing surveys,
        # test list and detail views (Enc, Surv, User)

    def test_get_success_url(self):
        """Expect: '/users/<pk>/'"""
        self.assertEqual(
            self.view.get_success_url(), "/users/{0}/".format(self.user.pk)
        )

    def test_get_object(self):
        """Expect: self.user, as that is the request's user object"""
        self.assertEqual(self.view.get_object(), self.user)

    def test_transfer_user(self):
        """Test transferring all objects owned by a user to another."""

        transfer_user(self.user, self.user2)
        self.assertEqual(self.user.encounters_reported.count(), 0)

    def test_transfer_area_user(self):
        """Test transferring all objects owned by a user to another."""

        change_user_for_area(self.user, self.user2, self.area)
        self.assertEqual(self.user.encounters_reported.count(), 0)
