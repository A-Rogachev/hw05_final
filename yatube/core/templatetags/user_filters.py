from typing import Any

from django import template
from django.template import Library


register: Library = template.Library()


@register.filter
def addclass(field: Any, css: Any) -> Any:
    """Фильтр добавляет класс к виджету формы"""

    return field.as_widget(attrs={"class": css})
