from django import forms
from django.contrib.auth import forms as au_forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='NameSurname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_use_correct_templates(self):
        """
        URL-адрес использует соответствующий шаблон.
        """
        addresses_templates = {
            'users:signup': 'users/signup.html',
            'users:login': 'users/login.html',
            'users:password_change': 'users/password_change_form.html',
            'users:password_change_done': 'users/password_change_done.html',
            'users:logout': 'users/logged_out.html',
            'users:password_change': 'users/password_change_form.html',
            'users:password_reset': 'users/password_reset_form.html',
            'users:password_reset_done': 'users/password_reset_done.html',
            'users:reset_done': 'users/password_reset_complete.html',
        }

        for address, template in addresses_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(
                    reverse(address)
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    'Адрес не возвращает корректный шаблон'
                    f' → адрес {address}, шаблон {template}.',
                )

                response = self.authorized_client.get(
                    reverse(
                        'users:reset_confirm',
                        kwargs={'uidb64': 'uidb64', 'token': 'token'},
                    ),
                )
                self.assertTemplateUsed(
                    response,
                    'users/password_reset_confirm.html',
                    'Функция <users:reset_confirm>'
                    ' не вовзращает корректный шаблон',
                )

    def test_signup_page_show_correct_context(self):
        """
        Шаблон create.html сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': au_forms.UsernameField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'Атрибут формы не соответствует ожидаемому',
                )
