from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User, UserCreationForm


class UserCreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.form = UserCreationForm()

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_register_user(self):
        """
        Валидная форма региструет нового пользователя.
        """
        users_count = User.objects.count()

        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Юзернейм',
            'email': 'example@yandex.ru',
            'password1': 'Pass123!',
            'password2': 'Pass123!',
        }

        self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            User.objects.count(),
            users_count + 1,
            'Количество пользователей не увеличилось.',
        )
        self.assertTrue(
            User.objects.filter(username=form_data['username']).exists(),
            'После регистрации пользователя, новая запись в БД не появилась.',
        )
