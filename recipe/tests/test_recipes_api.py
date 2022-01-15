from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from main_app.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')  # '(name of the app):(the url of lists)'


# helper functions
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
        'price': 5.90
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        # we don't need user here because it's public api request
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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
