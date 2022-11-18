from typing import Type

from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Класс возвращает страницу с формой для авторизации"""

    form_class: Type[CreationForm] = CreationForm
    success_url: str = reverse_lazy('posts:index')
    template_name: str = 'users/signup.html'
