import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Автор')

        cls.test_group = Group.objects.create(
            title='Group1',
            slug='grp1',
            description='Первая группа для тестирования формы',
        )

        cls.test_group_for_edit_page_testing = Group.objects.create(
            title='Group2',
            slug='grp2',
            description='Вторая группа для тестирования формы',
        )

        cls.test_post = Post.objects.create(
            text='Текст для проверки формы редактирования',
            group=cls.test_group,
            author=cls.author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def compare_attributes(self, form_data):
        for value, expected_value, field_name in form_data:
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    value,
                    expected_value,
                    'Значение атрибута не соответствует ожидаемому'
                    f' (атрибут {field_name})'
                )

    def test_create_post_form(self):
        """
        Валидная форма создает новый пост.
        """
        post_obj_identificators = set(
            Post.objects.values_list('pk', flat=True)
        )
        start_posts_count = len(post_obj_identificators)

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

        form_data = {
            'text': 'Текст для созданного для теста поста',
            'group': self.test_group.pk,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            Post.objects.count(),
            start_posts_count + 1,
            'Количество постов в БД не изменилось.'
        )

        new_pk = set(Post.objects.values_list('pk', flat=True)).difference(
            post_obj_identificators
        ).pop()

        recently_created_post = Post.objects.get(pk=new_pk)
        self.compare_attributes(
            [
                (
                    recently_created_post.text,
                    form_data['text'],
                    'текст',
                ),
                (
                    recently_created_post.group.pk,
                    form_data['group'],
                    'группа',
                ),
                (
                    recently_created_post.author.pk,
                    self.author.pk,
                    'автор',
                ),
                (
                    recently_created_post.image.read(),
                    gif_for_test,
                    'картинка',
                ),
            ]
        )

    def test_post_edit_form(self):
        """
        Запись в БД меняется корректно в случае отправки валидной формы.
        """
        url_for_edit = reverse('posts:post_edit', args=(self.test_post.pk, ))
        form_data = {
            'text': 'Измененный текст',
            'group': self.test_group_for_edit_page_testing.pk,
        }

        self.authorized_client.post(
            url_for_edit,
            data=form_data,
            follow=True,
        )

        edited_post = Post.objects.get(pk=self.test_post.pk)

        self.compare_attributes(
            [
                (
                    edited_post.text,
                    form_data['text'],
                    'текст',
                ),
                (
                    edited_post.group.pk,
                    form_data['group'],
                    'группа',
                ),
                (
                    edited_post.author.pk,
                    self.test_post.author.pk,
                    'автор',
                ),
            ]
        )

    def test_creating_comment_form(self):
        """
        Валидная форма создает новый комментарий.
        """
        comment_obj_identificators = set(
            Comment.objects.values_list('pk', flat=True)
        )
        start_comments_count = len(comment_obj_identificators)

        form_data = {
            'text': 'Текст тестового комментария',
        }

        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.test_post.pk},
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            Comment.objects.count(),
            start_comments_count + 1,
            'Количество комментариев в БД не изменилось.'
        )

        new_pk = set(Comment.objects.values_list('pk', flat=True)).difference(
            comment_obj_identificators
        ).pop()

        recently_created_comment = Comment.objects.get(pk=new_pk)

        self.compare_attributes(
            [
                (
                    recently_created_comment.text,
                    form_data['text'],
                    'текст комментария',
                ),
                (
                    recently_created_comment.post.pk,
                    self.test_post.pk,
                    'идентификатор комментируемого поста',
                ),
                (
                    recently_created_comment.author.pk,
                    self.author.pk,
                    'автор',
                ),
            ]
        )
