from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс возвращает страницу с инф-ией об авторе"""

    template_name: str = 'about/about.html'


class AboutTechView(TemplateView):
    """Класс возвращается страницу об используемых технологиях"""

    template_name: str = 'about/tech.html'
