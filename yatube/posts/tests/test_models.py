from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Текст для тестового комментария',
            author=cls.user,
            post=cls.post,
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """
        Проверяем, что у моделей корректно работает __str__.
        """
        str_method_results = [
            (
                self.group,
                self.group.title
            ),
            (
                self.post,
                self.post.text[:Post.LIMIT_OF_SYMBOLS_POST_STR]
            ),
            (
                self.comment,
                self.comment.text[:Comment.LIMIT_OF_SYMBOLS_COMMENT_STR]
            ),
            (
                self.follow,
                f'{self.user} подписан на {self.user}'
            )
        ]

        for model_obj, str_result in str_method_results:
            with self.subTest(model_obj=model_obj):
                self.assertEqual(
                    str(model_obj),
                    str_result,
                    'Метод __str__ неверно реализован'
                    f' для модели <{model_obj.__class__.__name__}>',
                )
        self.number = 'newNumber'

    def test_models_verbose_name(self):
        """
        verbose_name в полях совпадает с ожидаемым.
        """
        field_names_values_list = [
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        ]

        for field, expected_value in field_names_values_list:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                    'Значение атрибута verbose_name не соответствует'
                    f' ожидаемому для поля {field}'
                )

    def test_models_help_text(self):
        """
        help_text в полях совпадает с ожидаемым.
        """
        field_names_values = [
            (
                'text',
                'Введите текст поста',
            ),
            (
                'group',
                'Выберите группу',
            ),
        ]

        for field, expected_value in field_names_values:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value,
                    'Значение атрибута help_text не соответствует'
                    f' ожидаемому для поля {field}'
                )
