import datetime
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом."""
    return {
        'year': datetime.datetime.now().year,
    }
