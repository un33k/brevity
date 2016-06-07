from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse


class AdminURLTestCase(TestCase):
    def setUp(self):
        pass

    def test_admin_url(self):
        resp = self.client.get(reverse('admin:index'), follow=True)
        self.assertEqual(resp.status_code, 200)
