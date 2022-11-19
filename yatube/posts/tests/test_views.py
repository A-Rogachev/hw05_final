import enum
import math
import shutil
import tempfile
from random import randrange

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user(username='TheAuthor')
        cls.user_follower = User.objects.create_user(username='TheFollower')

        cls.test_group = Group.objects.create(
            title='Group1',
            slug='grp1',
            description='1ая группа для проведения тестирования',
        )
        cls.test_group_for_post_create_testing = Group.objects.create(
            title='Group2',
            slug='grp2',
            description='2ая группа для проведения тестирования',
        )

        gif_for_test = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='gif_for_test.gif',
            content=gif_for_test,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_author,
            group=cls.test_group,
            image=uploaded,
        )

        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user_author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user_author)
        cache.clear()

    def test_page_shows_correct_context(self):
        """
        Проверяем корректный контекст на страницах приложения.
        """
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_author,
        )

        self.auth_client.force_login(self.user_follower)

        urls_for_context_testing = [
            reverse(
                'posts:index',
            ),
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.test_group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author.username},
            ),
            reverse(
                'posts:follow_index',
            ),
        ]

        for url in urls_for_context_testing:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                testing_post = response.context['page_obj'].object_list[0]
                for field in self.post._meta.get_fields():
                    with self.subTest(field=field):
                        self.assertEqual(
                            getattr(testing_post, field.name, None),
                            getattr(self.post, field.name, None),
                            'Ошибка контекста'
                            f' при формировании страницы по адресу {url}.'
                        )

    def test_not_follower_context(self):
        """Проверяем верный контекст у _не_подписчика"""
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertNotIn(
            self.post,
            response.context['page_obj'].object_list,
            'Пост попал в неверную подписку.'
        )

    def test_right_context_for_group_profile_pages(self):
        """
        Проверяем корректный контекст на страницах
        группы и автора.
        """
        urls_context_list = [
            (
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': self.test_group.slug},
                ),
                self.test_group,
                'group',
            ),
            (
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user_author.username},
                ),
                self.user_author,
                'author',
            ),
        ]

        for url, model_obj, name in urls_context_list:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEquals(
                    response.context[0][name],
                    model_obj,
                    'Ошибка контекста'
                    f' (объект класса {model_obj} не был передан'
                    f'  в шаблон по адресу {url}.'
                )

    def test_new_post_not_in_wrong_group(self):
        """
        Проверяем, что созданный пост не попадает в
        неверную группу.
        """
        response = self.auth_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.test_group_for_post_create_testing.slug},
            ),
        )
        self.assertNotIn(
            self.post,
            response.context['page_obj'].object_list,
            'Созданный пост попал в неверную группу',
        )

    def test_post_detail_page_show_correct_context(self):
        """
        Шаблон post_detail.html сформирован с правильным контекстом.
        """
        response = self.auth_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            )
        )

        for field in self.post._meta.get_fields():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context['post'], field.name, None),
                    getattr(self.post, field.name, None),
                    'Ошибка контекста в шаблоне post_detail.html'
                    f' (поле {field}).'
                )

        for field in self.comment._meta.get_fields():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context['comments'][0], field.name, None),
                    getattr(self.comment, field.name, None),
                    'Ошибка контекста в шаблоне post_detail.html'
                    f' (поле {field}).'
                )

    def test_create_page_show_correct_context(self):
        """Шаблон create.html сформирован с правильным контекстом"""
        response = self.auth_client.get(reverse('posts:post_create'))
        self.assertIsInstance(
            response.context['form'],
            PostForm,
            'Ошибка контекста в шаблоне <create.html>.'
        )

    def test_post_edit_page_show_correct_context(self):
        """
        Форма редактирования поста, отфильтрованного по id.
        """
        response = self.auth_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': self.post.pk,
                }
            )
        )

        self.assertIsInstance(
            response.context['form'],
            PostForm,
            'Ошибка контекста в шаблоне <create.html>.'
        )

        self.assertEqual(
            response.context['form'].instance,
            self.post,
            'Ошибка в исходных значениях формы',
        )

    def test_check_cache_index_page(self):
        """
        Список постов на главной странице сохраняется в кэше.
        """
        text_of_test_post = self.post.text

        CheckLevels = enum.Enum(
            'CheckLevels',
            'before_removing_obj after_removing_obj after_cache_clear',
        )

        for level in CheckLevels:
            content = self.auth_client.get(
                reverse('posts:index')
            ).content

            args = (
                text_of_test_post,
                content.decode(),
                'Ошибка в кешировании страницы.',
            )

            if level == 'after_cache_clear':
                self.assertNotIn(*args)
            else:
                self.assertIn(*args)

            level == 'before_removing_obj' and Post.objects.filter(
                pk=self.post.pk
            ).delete()

            level == 'after_removing_obj' and cache.clear()


class FollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='Author')
        cls.follower = User.objects.create_user(username='Follower')

        cls.group = Group.objects.create(
            title='ТестоваяГруппа',
            slug='tst_grp',
            description='Группа для теста подписки на автора',
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.follower)

    def test_ability_following_authors(self):
        """
        Авторизованный пользователь может подписываться на других
        пользователей.
        """
        self.assertFalse(
            Follow.objects.filter(
                author=self.author.pk,
                user=self.follower.pk,
            ).exists(),
            'Подписка на автора уже существует'
        )

        self.client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username},
            )
        )

        self.assertTrue(
            Follow.objects.filter(
                author=self.author.pk,
                user=self.follower.pk,
            ).exists(),
            'Не создается подписка на автора'
        )

    def test_ability_unfollowing_authors(self):
        """
        Авторизованный пользователь может удалять из подписок
        других пользователей.
        """
        Follow.objects.create(
            author=self.author,
            user=self.follower,
        )

        self.client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username},
            )
        )

        self.assertFalse(
            Follow.objects.filter(
                author=self.author.pk,
                user=self.follower.pk,
            ).exists(),
            'Не удаляется подписка на автора'
        )


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user(username='TheAuthor')

        cls.test_group = Group.objects.create(
            title='TestGroup',
            slug='tstgroup',
            description='группа для тестирования паджинатора',
        )

        posts_for_paginator_testing = [
            Post(
                text='Текст поста',
                author=cls.user_author,
                group=cls.test_group,
            ) for number in range(randrange(settings.LIMIT_OF_RECORDS, 100))
        ]
        Post.objects.bulk_create(posts_for_paginator_testing)

        cls.posts_total = len(posts_for_paginator_testing)
        cls.number_of_pages = math.ceil(
            cls.posts_total / settings.LIMIT_OF_RECORDS
        )

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user_author)

    def test_paginator_works_properly(self):
        """
        Проверка работы паджинатора.
        """
        addresses_with_kwargs = {
            'posts:index': {},
            'posts:group_posts': {'slug': self.test_group.slug},
            'posts:profile': (
                {'username': self.user_author.username}
            ),
        }

        for address, kwargs in addresses_with_kwargs.items():
            with self.subTest(address=address):
                response = self.auth_client.get(
                    reverse(
                        address,
                        kwargs=kwargs,
                    )
                )

                num_of_posts_first_page = response.context[
                    'page_obj'
                ].paginator.get_page(1).object_list.count()

                num_of_posts_last_page = response.context[
                    'page_obj'
                ].paginator.get_page(self.number_of_pages).object_list.count()

                self.assertEqual(
                    num_of_posts_first_page,
                    settings.LIMIT_OF_RECORDS,
                    'Пагинатор работает некорректно'
                    f' по адресу {address}',
                )
                self.assertEqual(
                    num_of_posts_last_page,
                    (
                        self.posts_total
                        - (self.number_of_pages - 1)
                        * settings.LIMIT_OF_RECORDS
                    ),
                    'Пагинатор работает некорректно'
                    f' по адресу {address}',
                )
