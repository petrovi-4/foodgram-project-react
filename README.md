# Foodgram - сайт с вкусными рецептами!

![GitHub actions](https://github.com/petrovi-4/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## «Продуктовый помощник». 
Онлайн-сервис в котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии

- Python - 3.7
- Django - 3.2.13
- Django Rest Framework - 3.14
- Docker
- Docker Compose
- Nginx - 1.21.3
- Postgres - 15.1
- Gunicorn - 20.1

### Сервис доступен по адресу
```
https://158.160.20.150
```

### Запуск проекта
Для запуска проекта, в директории где лежит файл docker-compose.yml, создать файл .env с переменными окружения:

```
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к БД
POSTGRES_PASSWORD=postgres # пароль для подключения БД
DB_HOST=db # название сервиса
DB_PORT=5432 # порт для поделючения к БД
```
В директории infra/ выполнить команду:

```
docker compose up -d
```
Создаём суперпользователя:

```
docker compose exec backend python manage.py createsuperuser
```


![GitHub User's stars](https://img.shields.io/github/stars/petrovi-4?label=Stars&style=social)
![licence](https://img.shields.io/badge/licence-GPL--3.0-green)

