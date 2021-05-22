from django.test import TestCase
from django.urls import reverse


class AboutViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templ_pages_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }

    def test_about_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for templ, reverse_name in AboutViewTests.templ_pages_names.items():
            with self.subTest(template=templ, reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, templ)
