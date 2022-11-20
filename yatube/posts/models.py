from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель сообщества"""

    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Укажите название группы',
    )
    slug = models.SlugField(
        verbose_name='Slug для url-адреса',
        help_text='Укажите slug для url-адреса группы',
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Добавьте описание группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        """Возвращает название группы"""
        return self.title


class Post(models.Model):
    """Модель сообщения (публикация блога)"""

    LIMIT_OF_SYMBOLS_POST_STR: int = 15

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Выберите группу',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        """Возвращает первые 15 символов текста поста"""
        return self.text[:self.LIMIT_OF_SYMBOLS_POST_STR]


class Comment(models.Model):
    """Модель комментария для публикации"""

    LIMIT_OF_SYMBOLS_COMMENT_STR: int = 15

    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст коммментария',
    )

    created = models.DateTimeField(
        verbose_name='Дата создания комментария',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """Возвращает первые 15 символов комментария"""
        return self.text[:self.LIMIT_OF_SYMBOLS_COMMENT_STR]


class Follow(models.Model):
    """Модель подписки"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор контента',
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self) -> str:
        """Строковое представление подписки"""
        return f'{self.user} подписан на {self.author}'
