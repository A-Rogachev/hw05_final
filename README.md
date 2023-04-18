<a id='start'></a>
# <p align = center>Yatube</p>
###### Социальная сеть для блогеров.
___
*   Создание страницы автора с правом выбора имени и уникального адреса для страницы. 
* Публикация личных дневников, возможность комментирования записей и подписки на авторов.

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/downloads/release/python-379/)
[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=djangologoColor=white)](https://docs.djangoproject.com/en/4.1/releases/2.2.19/)


<font size=3> ► [Python 3.7.9](https://www.python.org/downloads/release/python-379/)  
► [Django 2.2.19](https://docs.djangoproject.com/en/4.1/releases/2.2.19/)</font>


#### Как запустить проект:
1. Клонировать репозиторий и перейти в него в терминале:
```
git clone https://github.com/A-Rogachev/hw05_final.git
```
```
cd hw05_final
```
2. Создать и активировать виртуальное окружение.
```
python3 -m venv env
```
```
source env/bin/activate
```
3. Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
4. Выполнить миграции:
```
python3 manage.py migrate
```
5. Запустить проект:
 ```
python3 manage.py runserver
```

#### Автор

><font size=2>Рогачев А.Г.  
Студент факультета Бэкенд. Когорта № 50</font>

 
  
[вверх](#start)

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
