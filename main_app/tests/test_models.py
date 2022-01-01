from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with and email is successful"""
        email = 'test@gmail.com'
        password = '12345'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        # check_password() is django user function with check if the entered password is the same or not
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@FATEME.com'
        user = get_user_model().objects.create_user(
            email=email,
            password='1234567fateme'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test: creating a new user with no email, raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password='123')

    def test_new_user_invalid_password(self):
        """Test: creating a new user with no password, raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='fateme@gmail.CoM', password=None)

    def test_create_new_superuser(self):
        """Test: creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='superuser@email.cOM',
            password='1534'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
