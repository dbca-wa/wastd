from test_plus.test import TestCase
from users.admin import UserCreationForm


class TestUserCreationForm(TestCase):
    def setUp(self):
        self.user = self.make_user()

    def test_clean_username_success(self):
        # Instantiate the form with a new username
        form = UserCreationForm(
            {
                "username": "alamode",
                "password1": "123456",
                "password2": "123456",
            }
        )
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

        # Run the actual clean_username method
        username = form.clean_username()
        self.assertEqual("alamode", username)

    def test_clean_username_false(self):
        # Instantiate the form with the same username as self.user
        form = UserCreationForm(
            {
                "username": self.user.username,
                "password1": "123456",
                "password2": "123456",
            }
        )
        # Run is_valid() to trigger the validation, which is going to fail
        # because the username is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'username'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue("username" in form.errors)
