from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """Класс для создания формы регистрации пользователя"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
