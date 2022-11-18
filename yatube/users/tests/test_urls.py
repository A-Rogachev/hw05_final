from collections import namedtuple
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_exist_at_desired_location(self):
        """
        Проверяем доступность страниц приложения <users>
        для разных типов учетных записей.
        """
        users_urls_clients_list = {
            '/auth/signup/': self.guest_client,
            '/auth/login/': self.guest_client,
            '/auth/logout/': self.guest_client,
            '/auth/password_reset/': self.guest_client,
            '/auth/password_reset/done/': self.guest_client,
            '/auth/reset/done/': self.guest_client,
            '/auth/password_change/': self.authorized_client,
            '/auth/password_change/done/': self.authorized_client,
            '/auth/reset/some_uidb64/some_token/': self.authorized_client,
        }

        for url, client in users_urls_clients_list.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Страница не доступна по адресу'
                    f' ({url} для пользователя {client}).',
                )

    def test_users_urls_redirects_guest_users(self):
        """
        Проверяем перенаправление для незарегистрированного пользователя.
        """
        urls_redirects_list = {
            '/auth/password_change/': (
                '/auth/login/?next=/auth/password_change/'
            ),
            '/auth/password_change/done/': (
                '/auth/login/?next=/auth/password_change/done/'
            ),
        }

        for url, redirect_url in urls_redirects_list.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    redirect_url,
                )

    def test_urls_use_correct_template_for_all_users(self):
        """
        Проверяем, что URL-адрес использует соответствующий шаблон.
        """
        AdditionalData = namedtuple('AdditionalData', ['template', 'client'])

        urls_templates_clients = {
            '/auth/signup/': AdditionalData(
                'users/signup.html',
                self.guest_client,
            ),
            '/auth/login/': AdditionalData(
                'users/login.html',
                self.guest_client,
            ),
            '/auth/logout/': AdditionalData(
                'users/logged_out.html',
                self.guest_client,
            ),
            '/auth/password_reset/': AdditionalData(
                'users/password_reset_form.html',
                self.guest_client,
            ),
            '/auth/password_reset/done/': AdditionalData(
                'users/password_reset_done.html',
                self.guest_client,
            ),
            '/auth/reset/done/': AdditionalData(
                'users/password_reset_complete.html',
                self.guest_client,
            ),
            '/auth/password_change/': AdditionalData(
                'users/password_change_form.html',
                self.authorized_client,
            ),
            '/auth/password_change/done/': AdditionalData(
                'users/password_change_done.html',
                self.authorized_client,
            ),
            '/auth/reset/some_uidb64/some_token/': AdditionalData(
                'users/password_reset_confirm.html',
                self.authorized_client,
            ),
        }

        for url, add_info in urls_templates_clients.items():
            with self.subTest(url=url):
                response = add_info.client.get(url)
                self.assertTemplateUsed(
                    response,
                    add_info.template,
                    'Ошибка - адрес не возвращает ожидаемый шаблон'
                    f' (адрес {url}, шаблон {add_info.template}',
                )
