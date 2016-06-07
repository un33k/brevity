from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.test import Client

from rest_framework import status

from ..utils.common import get_url_name

User = get_user_model()


class GenericsCsrfRetrieveTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.data = {'email': '1@foo.com', 'password': 'hello'}
        self.user = User.objects.create_user(**self.data)
        self.assertEqual(self.user.email, self.data['email'])
        self.csrf_url = reverse(get_url_name(__name__, 'api-generics-csrf-retrieve'))

    def login(self):
        return self.client.login(username=self.data['email'],
            password=self.data['password'])

    def test_csrftoken_get_request_anonymous(self):
        """
        GET is not allowed for anonymous user.
        """
        resp = self.client.get(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_csrftoken_get_request_authenticated(self):
        """
        GET is not allowed for authenticated user.
        """
        authenticated = self.login()
        self.assertEqual(authenticated, True)
        resp = self.client.get(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_csrftoken_post_request_anonymous(self):
        """
        CSRF token for anonymous user
        """
        resp = self.client.post(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual('csrf_token' in resp.data, True)
        self.assertNotEqual(len(resp.data['csrf_token'].strip()), 0)
        self.anonymous_csrf_token = resp.data['csrf_token']

    def test_csrftoken_post_request_authenticated(self):
        """
        POST is allowed for authenticate user. CSRF is rotated on login.
        """
        resp = self.client.post(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        csrftoken_anonymous = resp.data['csrf_token']
        csrftoken_anonymous_cookie = self.client.cookies['csrftoken'].value
        self.assertEqual(csrftoken_anonymous_cookie, csrftoken_anonymous)

        self.login()

        #  send a post without csrfmiddlewaretoken
        resp = self.client.post(self.csrf_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        #  send a post with csrfmiddlewaretoken
        resp = self.client.post(self.csrf_url, {'csrfmiddlewaretoken': csrftoken_anonymous})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
