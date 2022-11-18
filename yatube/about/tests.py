from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """
        Проверяем доступность страниц приложения <about>.
        """

        about_urls = (
            '/about/author/',
            '/about/tech/',
        )

        for url in about_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Страница не доступна по адресу'
                    f' → {url}.',
                )

    def test_about_urls_use_correct_templates(self):
        """
        Проверяем, что URL-адрес использует соответствующий шаблон.
        """
        urls_templates = {
            '/about/author/': 'about/about.html',
            '/about/tech/': 'about/tech.html',
        }

        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка - адрес не возвращает ожидаемый шаблон'
                    f' (адрес {url}, шаблон {template}',
                )


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_uses_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        pages_templates_names = {
            'about:author': 'about/about.html',
            'about:tech': 'about/tech.html',
        }

        for address, template in pages_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(
                    response,
                    template,
                    'Адрес не возвращает корректный шаблон'
                    f' → адрес {address}, шаблон {template}.',
                )
