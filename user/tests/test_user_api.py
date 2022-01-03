from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# constant values which we define at the first of the code.
# url to create user
CREATE_USER_URL = reverse('user:create')
# url to generate the user token
TOKEN_URL = reverse('user:token')
# update user endpoint url  user/"me" => the account of the user who is authenticated
ME_URL = reverse('user:me')


# helper function
def create_user_customized(**params):  # **params is a dynamic list of arguments & makes lines a little shorter.
    return get_user_model().objects.create_user(**params)


# public api is not authenticated (without creating user and logging in)
class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        # we just make a client for aur test here,
        # so we don't need to make any in this test.
        # and we can reuse it in all the tests.
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        # the payload is an object which you pass to an API when you make the request.
        payload = {
            'email': 'falkel@gmail.com',
            'password': '123eret4',
            'name': 'fateme'
        }
        # lets make our request (http post request):
        res = self.client.post(CREATE_USER_URL, payload)  # this res return "a created user"

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'falkel@gmail.com', 'password': '1234er'}

        # we put ** before the name of dictionary to make it cleaner as arguments of function.
        # it means we created a user with this info before we send post request to create page.
        create_user_customized(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'falkel@gmail.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    # --------------------------------------- user token tests

    def test_create_token_for_user(self):
        """Test that a token created for the user"""
        payload = {'email': 'falkel@gmail.com', 'password': '12344w5'}
        # we are going to create a user by helper function that match this authentication, so we can test it.
        create_user_customized(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user_customized(email='fateme@test.com', password='testpass')
        payload = {'email': 'fateme@test.com', 'password': 'passnotthesame'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = {'email': 'fateme@test.com', 'password': 'passtest'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------manage user tests

    # the authentication is required for the endpoint (it's an important part)
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# authentication is required before you can use those points.
# private api is like modifying user or making some change in user.
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        """Set the Authentication for whole tests in this class"""
        self.user = create_user_customized(
            email='test3@hotmail.com',
            password='testpass2',
            name='fateme3'
        )
        # Just make reusable client
        self.client = APIClient()
        # to forcte to authenticate any requests that the client makes with our sample user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # res does not send the hash password it only sends email and name
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new_name', 'password': 'new_password'}
        res = self.client.patch(ME_URL, payload)

        # a helper function which refresh database by latest values
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
