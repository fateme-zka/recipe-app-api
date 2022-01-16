from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from main_app.models import *


# helper function
def sample_user(email='test@gmail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


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

    # ---------------------------- tag model tests
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = Tag.objects.create(user=sample_user(), name='Vegan')

        self.assertEqual(str(tag), tag.name)  # Tag model should return name in __str__ function

    # ---------------------------- ingredient model tests
    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # ----------------------------- test Recipe model
    def test_recipe_str(self):
        """Test the recipe model string the representation"""
        recipe = Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    # -----------------------test image field of recipe model
    @patch('uuid.uuid4')  # uuid4 is a function in uuid module
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None, 'my_image.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(exp_path, file_path)
