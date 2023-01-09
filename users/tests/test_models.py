from test_plus.test import TestCase


class TestUser(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test__str__(self):
        self.assertTrue(self.user.username in self.user.__str__())

    def test_get_absolute_url(self):
        self.assertEqual(
            self.user.get_absolute_url(), "/users/{0}/".format(self.user.pk)
        )

    def test_apitoken(self):
        t = self.user.apitoken
        self.assertIsNotNone(t)
