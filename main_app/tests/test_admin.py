from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    # this setup function that is ran BEFORE every tests that we run
    def setUp(self):
        """
        this function is going to consist of creating our test clients
        we're going to add new users which we can use to test.
        and we're going to make sure the user is logged into our client.
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser('admin@gmail.com', '321')

        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='4325',
            name='test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""

        # this url generates an url for our list user page.
        # we write it like this cause if we will change the url nothing need to change here.
        url = reverse('admin:main_app_user_changelist')
        # res is this url http. (this get function gets the http of this url)
        res = self.client.get(url)

        # check if res page has(contains) this self.user.name and also check if http response status code is 200 or not.
        # actually this checks res content to contain this objects
        # because res actually is just an object
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:main_app_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:main_app_user_add')  # this is standard url to add new user page for all projects.
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
