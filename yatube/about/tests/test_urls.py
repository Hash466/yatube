from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls_pages_names = {
            '/about/author/': 'about:author',
            '/about/tech/': 'about:tech',
        }

    def test_url_pages_reverse(self):
        """Абсолютный URL-адрес соответствует reverse."""
        for absolute_url, name in self.urls_pages_names.items():
            with self.subTest(absolute_url=absolute_url,
                              reverse_url=name):
                self.assertEqual(absolute_url, reverse(name))

    def test_url_exists_at_desired_location(self):
        """Доступный URL-адрес."""
        for address in self.urls_pages_names.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
