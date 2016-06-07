import json
from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from rest_framework import status

from ..utils.common import get_url_name

User = get_user_model()


class ProfileCreateTestCase(TestCase):
    def setUp(self):
        self.url = reverse(get_url_name(__name__, 'api-profile-create'))

    def test_create_with_valid_email(self):
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': 'hello',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_with_invalid_email(self):
        resp = self.client.post(self.url, {
            'email': '1@foocom',
            'password': 'hello',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_duplicate_email(self):
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': 'hello',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': 'hello',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.client.post(self.url, {
            'email': '1@FOO.com',
            'password': 'hello',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_no_password(self):
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_empty_password(self):
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': '',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_extended_info(self):
        data = {
            'email': '1@foo.com',
            'password': 'hello',
            'first_name': 'Mike',
            'last_name': 'Mike Tyson',
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('email'), '1@foo.com')
        self.assertEqual(resp.data.get('first_name'), 'Mike')
        self.assertEqual(resp.data.get('last_name'), 'Mike Tyson')
        self.assertNotEqual(len(resp.data.get('username')), 0)

    def test_create_with_custom_username(self):
        data = {
            'email': '1@foo.com',
            'password': 'hello',
            'username': 'mike-tyson',
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data.get('username'), 'mike-tyson')

    def test_create_with_duplicate_username(self):
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': 'hello',
            'username': 'mike-tyson',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(self.url, {
            'email': '1@foo.com',
            'password': 'hello',
            'username': 'Mike-Tyson',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileRetrieveTestCase(TestCase):
    def setUp(self):
        # Create a normal user 1
        self.data1 = {
            'email': '1@foo.com',
            'password': 'hello',
        }
        self.user1 = User.objects.create_user(**self.data1)
        self.assertEqual(self.user1.email, self.data1['email'])

        # Create a normal user 2
        self.data2 = {
            'email': '2@foo.com',
            'password': 'hello',
        }
        self.user2 = User.objects.create_user(**self.data2)
        self.assertEqual(self.user2.email, self.data2['email'])

    def test_retrieve_self_unauthenticated(self):
        """
        Not logged in and not using 'pk'. (deny)
        """
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'))
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_self_authenticated(self):
        """
        Logged in and not using 'pk'. (allow)
        """
        authenticated = self.client.login(username=self.data1['email'],
            password=self.data1['password'])
        self.assertTrue(authenticated)
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'))
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_retrieve_self_by_pk_authenticated(self):
        """
        Logged in and using 'pk'. (allow)
        """
        authenticated = self.client.login(username=self.data1['email'],
            password=self.data1['password'])
        self.assertTrue(authenticated)
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'),
            kwargs={'pk': self.client.session['_auth_user_id']})
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], self.data1.get('email'))

    def test_retrieve_others_by_pk_authenticated(self):
        """
        Logged in and using not self 'pk'. (deny)
        """
        authenticated = self.client.login(username=self.data1['email'],
            password=self.data1['password'])
        self.assertTrue(authenticated)
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'),
            kwargs={'pk': self.user2.id})
        resp = self.client.get(retrieve_url)
        # self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ProfileRetrieveSuperuserTestCase(TestCase):
    def setUp(self):
        # Create a super user
        self.admin = {
            'email': 'admin@foo.com',
            'password': 'hello',
        }
        self.superuser = User.objects.create_superuser(**self.admin)
        self.assertEqual(self.superuser.email, self.admin['email'])
        self.assertTrue(self.superuser.is_superuser)

        # Create a normal user
        self.data = {
            'email': '1@foo.com',
            'password': 'hello',
        }
        self.user = User.objects.create_user(**self.data)
        self.assertEqual(self.user.email, self.data['email'])

    def test_retrieve_others_by_pk_authenticated_superuser(self):
        # Log in as super user
        authenticated = self.client.login(username=self.admin['email'],
            password=self.admin['password'])
        self.assertTrue(authenticated)

        # Retrieve a non-existing user
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'),
            kwargs={'pk': 99999})
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Retrieve an existing user
        retrieve_url = reverse(get_url_name(__name__, 'api-profile-retrieve'),
            kwargs={'pk': self.user.id})
        resp = self.client.get(retrieve_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ProfileUpdateTestCase(TestCase):
    def setUp(self):
        # Create a super user
        self.admin = {
            'email': 'admin@foo.com',
            'password': 'hello',
        }
        self.superuser = User.objects.create_superuser(**self.admin)
        self.assertEqual(self.superuser.email, self.admin['email'])
        self.assertTrue(self.superuser.is_superuser)

        # Create a normal user
        self.data = {
            'email': '1@foo.com',
            'password': 'hello',
        }
        self.user = User.objects.create_user(**self.data)
        self.assertEqual(self.user.email, self.data['email'])

    def test_update_self_unauthenticated(self):
        """
        Not logged in and updating. (deny)
        """
        update_url = reverse(get_url_name(__name__, 'api-profile-update'),
            kwargs={'pk': self.user.id})
        data = {'first_name': 'Mike', 'last_name': 'Tyson', 'username': 'zEDZZDEZD'}
        resp = self.client.put(update_url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_self_authenticated(self):
        """
        Logged in and updating self. (allow)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.data['email'],
            password=self.data['password'])
        self.assertTrue(authenticated)

        # Update user
        update_url = reverse(get_url_name(__name__, 'api-profile-update'),
            kwargs={'pk': self.user.id})
        data = {'first_name': 'Mike', 'last_name': 'Tyson', 'username': 'zEDZZDEZD'}
        resp = self.client.put(update_url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Check response for update
        self.assertEqual(resp.data['first_name'], data['first_name'])
        self.assertEqual(resp.data['last_name'], data['last_name'])
        self.assertEqual(resp.data['username'], data['username'])

        # Check database for update
        self.user = User.objects.get(email=self.data['email'])
        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.last_name, data['last_name'])
        self.assertEqual(self.user.username, data['username'])

    def test_update_others_authenticated(self):
        """
        Logged in and updating others. (deny)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.data['email'],
            password=self.data['password'])
        self.assertTrue(authenticated)

        # Update user
        update_url = reverse(get_url_name(__name__, 'api-profile-update'),
            kwargs={'pk': self.superuser.id})
        data = {'first_name': 'Mike', 'last_name': 'Tyson', 'username': 'zEDZZDEZD'}
        resp = self.client.put(update_url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_others_authenticated_as_superuser(self):
        """
        Logged in and updating others. (allow)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.admin['email'],
            password=self.admin['password'])
        self.assertTrue(authenticated)

        # Update user
        update_url = reverse(get_url_name(__name__, 'api-profile-update'),
            kwargs={'pk': self.user.id})
        data = {'first_name': 'Mike', 'last_name': 'Tyson', 'username': 'zEDZZDEZD'}
        resp = self.client.put(update_url, data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class ProfileDeleteTestCase(TestCase):
    def setUp(self):
        # Create a super user
        self.admin = {
            'email': 'admin@foo.com',
            'password': 'hello',
        }
        self.superuser = User.objects.create_superuser(**self.admin)
        self.assertEqual(self.superuser.email, self.admin['email'])
        self.assertTrue(self.superuser.is_superuser)

        # Create a normal user
        self.data = {
            'email': '1@foo.com',
            'password': 'hello',
        }
        self.user = User.objects.create_user(**self.data)
        self.assertEqual(self.user.email, self.data['email'])

    def test_delete_self_unauthenticated(self):
        """
        Not logged in and deleting self. (deny)
        """
        delete_url = reverse(get_url_name(__name__, 'api-profile-delete'),
            kwargs={'pk': self.user.id})
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_self_authenticated(self):
        """
        Logged in and deleting self. (allow)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.data['email'],
            password=self.data['password'])
        self.assertTrue(authenticated)

        # Delete self
        delete_url = reverse(get_url_name(__name__, 'api-profile-delete'),
            kwargs={'pk': self.user.id})
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Try to login again
        authenticated = self.client.login(username=self.data['email'],
            password=self.data['password'])
        self.assertFalse(authenticated)

        # Check database for deleted user
        users = User.objects.filter(email=self.data['email'])
        self.assertEqual(len(users), 0)

    def test_delete_others_authenticated_as_superuser(self):
        """
        Logged in as admin and deleting others. (allow)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.admin['email'],
            password=self.admin['password'])
        self.assertTrue(authenticated)

        # Delete self
        delete_url = reverse(get_url_name(__name__, 'api-profile-delete'),
            kwargs={'pk': self.user.id})
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Try to login again
        authenticated = self.client.login(username=self.data['email'],
            password=self.data['password'])
        self.assertFalse(authenticated)

        # Check database for deleted user
        users = User.objects.filter(email=self.data['email'])
        self.assertEqual(len(users), 0)

    def test_delete_self_authenticated_as_superuser(self):
        """
        Logged in as admin and deleting self. (deny)
        """
        # Login as normal user
        authenticated = self.client.login(username=self.admin['email'],
            password=self.admin['password'])
        self.assertTrue(authenticated)

        # Delete self
        delete_url = reverse(get_url_name(__name__, 'api-profile-delete'),
            kwargs={'pk': self.superuser.id})
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Try to login again
        authenticated = self.client.login(username=self.admin['email'],
            password=self.admin['password'])
        self.assertTrue(authenticated)

        # Check database for deleted user
        users = User.objects.filter(email=self.admin['email'])
        self.assertEqual(len(users), 1)
