from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Класс для формы создания/редактирования постов"""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': "Текст нового поста",
            'group': "Группа, к которой будет относиться пост",
        }


class CommentForm(forms.ModelForm):
    """Класс для формы создания комментария"""

    class Meta:
        model = Comment
        fields = ('text', )
