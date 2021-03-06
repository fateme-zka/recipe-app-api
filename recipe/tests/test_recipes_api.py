from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from main_app.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os

from PIL import Image

RECIPES_URL = reverse('recipe:recipe-list')  # '(name of the app):(the url of lists)'


# helper functions

def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])
    # to pass in arguments to our url & you can pass in multiple args in []


def sample_tag(user, name="Main Course"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(name=name, user=user)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'sample_recipe',
        'time_minutes': 10,
        'price': 50
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


# *************************************************************************
class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        # we don't need user here because it's public api request
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# *************************************************************************
class PrivateRecipeApiTests(TestCase):
    """Test authenticated API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            name='sample_user',
            email='sample@gmail.com',
            password='testpassword1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        sample_recipe(user=self.user, title='Kebab')
        sample_recipe(user=self.user, title='Spaghetti')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()  # .order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that the recipe list is limited to authenticated user"""
        user2 = get_user_model().objects.create_user('user2@gmail.com', 'passworduser2123')

        recipe = sample_recipe(user=self.user, title='Sushi')
        sample_recipe(user=user2, title='Spaghetti')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)
        self.assertEqual(res.data, serializer.data)

    # ----------------------------------------------- test retrieving recipe detail
    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        user_tag = sample_tag(user=self.user)
        recipe.tags.add(user_tag)
        user_ingredient = sample_ingredient(user=self.user)
        recipe.ingredients.add(user_ingredient)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    # ------------------------------------------------ test create a new recipe
    def test_create_basic_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'New recipe',
            'time_minutes': 10,
            'price': 59
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # in creation method response return a dictionary which contains a data of an object that created
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        # self.assertEqual(recipe.title, payload['title'])
        # self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        # self.assertEqual(recipe.price, payload['price'])

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 70,
            'price': 98
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()  # this is a queryset of tags of this recipe

        self.assertEqual(tags.count(), 2)
        # self.assertEqual(tags.values_list('id'), payload['tags'])
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Salt')
        ingredient2 = sample_ingredient(user=self.user, name='Sugar')

        payload = {
            'title': 'Avocado khoresht',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 70,
            'price': 48
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # ------------------------------------------------ test updating recipe
    # in PATCH update method only the changed fields will be updated not all fields
    # in PUT method all fields will update, because all previous fields will be removed from that object
    def test_partial_update_recipe(self):
        """Test updating a recipe with PATCH"""
        recipe = sample_recipe(user=self.user)
        user_tag = sample_tag(user=self.user)
        recipe.tags.add(user_tag)
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka', 'tags': new_tag.id}

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()  # refreshing the recipe from the database

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertIn(new_tag, tags)
        self.assertEqual(len(tags), 1)

    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        user_tag = sample_tag(user=self.user)
        recipe.tags.add(user_tag)

        payload = {
            'title': 'Chicken tikka',
            'time_minutes': 24,
            'price': 456
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()  # refreshing the recipe from the database

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])

        tags = recipe.tags.all().count()
        ingredients = recipe.ingredients.all().count()
        self.assertEqual(tags, 0)
        self.assertEqual(ingredients, 0)


# ***********************************************************************************
class RecipeImageUploadTests(TestCase):

    # setUp runs before all tests start to run
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='sample@gmail.com',
            password='testpassword1234'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    # after tests run tearDown function will run
    def tearDown(self):
        """To check that all the tests stuffs is removed from project or no"""
        self.recipe.image.delete()
        # so now we can be confident that there is no image in our recipe

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            image = Image.new('RGB', (10, 10))
            image.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'no-image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
