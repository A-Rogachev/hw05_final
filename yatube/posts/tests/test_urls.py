from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='TheAuthor',
        )
        cls.user_not_the_author = User.objects.create_user(
            username='NotTheAuthor',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Test_post',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_posts_urls_match_reverses(self):
        """
        Проверяем соответствие фактических адресов
        страниц с их именами.
        """
        urls_reverses_list = [
            (
                '/',
                reverse('posts:index'),
            ),
            (
                f'/group/{self.group.slug}/',
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': self.group.slug},
                ),
            ),
            (
                f'/profile/{self.user_author.username}/',
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user_author.username},
                ),
            ),
            (
                f'/posts/{self.post.pk}/',
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk},
                ),
            ),
            (
                '/create/',
                reverse('posts:post_create'),
            ),
            (
                f'/posts/{self.post.pk}/edit/',
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk},
                ),
            ),
            (
                f'/posts/{self.post.pk}/comment/',
                reverse(
                    'posts:add_comment',
                    kwargs={'post_id': self.post.pk},
                ),
            ),
            (
                '/follow/',
                reverse(
                    'posts:follow_index',
                ),
            ),
            (
                f'/profile/{self.user_author.username}/follow/',
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': self.user_author.username},
                ),
            ),
            (
                f'/profile/{self.user_author.username}/unfollow/',
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': self.user_author.username},
                ),
            ),
        ]

        for url, url_from_reverse in urls_reverses_list:
            with self.subTest(url=url):
                self.assertEquals(
                    url,
                    url_from_reverse,
                    'Ошибка соответствия фактического адреса страницы'
                    f' с ее именем → {url} != {url_from_reverse}',
                )

    def test_posts_urls_exist_at_desired_location(self):
        """
        Проверяем доступность страниц приложения <posts>
        для разных типов учетных записей.
        """
        address_status_client_list = [
            (
                reverse('posts:index'),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': self.group.slug},
                ),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user_author.username},
                ),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk},
                ),
                HTTPStatus.OK,
                self.guest_client,
            ),
            (
                reverse('posts:post_create'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk},
                ),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                '/unexisting_page/',
                HTTPStatus.NOT_FOUND,
                self.guest_client,
            ),
            (
                reverse(
                    'posts:follow_index',
                ),
                HTTPStatus.OK,
                self.authorized_client,
            ),
        ]

        for address, expected_status, client in address_status_client_list:
            with self.subTest(address=address):
                response = client.get(address)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                    'Код состояния HTTP не соответствует ожидаемому'
                    f' ({address} для пользователя {client}).',
                )

    def test_posts_urls_use_correct_templates(self):
        """
        Проверяем, что URL-адрес использует соответствующий шаблон.
        """
        urls_templates_list = [
            (
                reverse('posts:index'),
                'posts/index.html',
            ),
            (
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': self.group.slug},
                ),
                'posts/group_list.html',
            ),
            (
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user_author.username},
                ),
                'posts/profile.html',
            ),
            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk},
                ),
                'posts/post_detail.html',
            ),
            (
                reverse('posts:post_create'),
                'posts/create_post.html',
            ),
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk},
                ),
                'posts/create_post.html',
            ),
            (
                reverse(
                    'posts:follow_index',
                ),
                'posts/follow.html',
            ),
            (
                '/unexisting_page/',
                'core/404.html',
            )
        ]

        for url, template in urls_templates_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Ошибка - адрес не возвращает ожидаемый шаблон'
                    f' (адрес {url}, шаблон {template}',
                )

    def test_post_list_url_correctly_redirect_clients(self):
        """
        Проверяем перенаправления для разных учетных записей.
        """
        self.authorized_client.force_login(self.user_not_the_author)

        urls_redirects_list = [
            (
                reverse(
                    'posts:post_create',
                ),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse("posts:post_create"),
                ),
                self.guest_client,
            ),
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk},
                ),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse(
                        "posts:post_edit",
                        kwargs={"post_id": self.post.pk},
                    )
                ),
                self.guest_client,
            ),
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.pk},
                ),
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.pk},
                ),
                self.authorized_client
            ),
            (
                reverse(
                    'posts:add_comment',
                    kwargs={'post_id': self.post.pk},
                ),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse(
                        "posts:add_comment",
                        kwargs={"post_id": self.post.pk},
                    )
                ),
                self.guest_client
            ),
            (
                reverse('posts:follow_index'),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse('posts:follow_index'),
                ),
                self.guest_client,
            ),
            (
                reverse('posts:follow_index'),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse('posts:follow_index'),
                ),
                self.guest_client,
            ),
            (
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': self.user_author.username},
                ),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse(
                        'posts:profile_follow',
                        kwargs={'username': self.user_author.username},
                    ),
                ),
                self.guest_client,
            ),
            (
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': self.user_author.username},
                ),
                '{}?next={}'.format(
                    reverse("users:login"),
                    reverse(
                        'posts:profile_unfollow',
                        kwargs={'username': self.user_author.username},
                    ),
                ),
                self.guest_client,
            ),
        ]

        for url, redirect_url, client in urls_redirects_list:
            with self.subTest(url=url):
                response = client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    redirect_url,
                )
