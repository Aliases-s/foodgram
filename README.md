cat > README.md << 'EOF'
# Фудграм

Сайт для публикации рецептов. Пользователи могут делиться своими
рецептами, добавлять чужие в избранное, подписываться на авторов
и формировать список покупок, который можно скачать файлом.

## Адрес проекта

https://alina-foodgram.duckdns.org

Документация API: https://alina-foodgram.duckdns.org/api/docs/

## Возможности

- Регистрация и авторизация по токену
- Публикация, редактирование и удаление своих рецептов
- Добавление рецептов в избранное и список покупок
- Скачивание списка покупок в формате .txt с суммированием
  повторяющихся ингредиентов
- Подписка на авторов и лента их публикаций
- Фильтрация рецептов по тегам
- Короткие ссылки на рецепты
- Загрузка и удаление аватара профиля

## Стек технологий

- Python 3.12, Django 4.2, Django REST Framework
- Djoser, django-filter, Pillow
- PostgreSQL 13
- Gunicorn, Nginx
- Docker, Docker Compose
- GitHub Actions

## Локальный запуск

Клонировать репозиторий и перейти в папку с бэкендом:
```
git clone https://github.com/Aliases-s/foodgram.git
cd foodgram/backend
```

Создать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости:
```
pip install -r requirements.txt
```

Создать файл `.env` по образцу `.env.example`. Для локальной работы
на SQLite добавить в него строку `USE_SQLITE=True`.

Выполнить миграции и загрузить ингредиенты:
```
python manage.py migrate
python manage.py load_ingredients
python manage.py createsuperuser
```

Запустить сервер разработки:
```
python manage.py runserver
```

## Запуск в Docker

В корне проекта должен лежать файл `.env` с переменными окружения.
```
docker compose -f docker-compose.production.yml up -d
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Переменные окружения

| Переменная | Назначение |
|---|---|
| SECRET_KEY | секретный ключ Django |
| DEBUG | режим отладки, False на продакшене |
| ALLOWED_HOSTS | список доменов через запятую |
| POSTGRES_DB | имя базы данных |
| POSTGRES_USER | пользователь базы данных |
| POSTGRES_PASSWORD | пароль пользователя базы данных |
| DB_HOST | адрес базы данных |
| DB_PORT | порт базы данных |
| USE_SQLITE | True для локальной разработки на SQLite |

## Примеры запросов к API

Получение списка рецептов:
```
GET /api/recipes/
```

Ответ:
```
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tags": [{"id": 1, "name": "Завтрак", "slug": "breakfast"}],
      "author": {
        "email": "user@example.com",
        "id": 1,
        "username": "user",
        "first_name": "Имя",
        "last_name": "Фамилия",
        "is_subscribed": false,
        "avatar": null
      },
      "ingredients": [
        {
          "id": 1,
          "name": "картофель",
          "measurement_unit": "г",
          "amount": 500
        }
      ],
      "is_favorited": false,
      "is_in_shopping_cart": false,
      "name": "Запечённый картофель",
      "image": "https://alina-foodgram.duckdns.org/media/recipes/1.png",
      "text": "Описание рецепта",
      "cooking_time": 40
    }
  ]
}
```

Получение токена:
```
POST /api/auth/token/login/
{
  "email": "user@example.com",
  "password": "password"
}
```

Добавление рецепта в избранное:
```
POST /api/recipes/1/favorite/
Authorization: Token <токен>
```

## CI/CD

При пуше в ветку `main` GitHub Actions проверяет код на соответствие
PEP 8, собирает образы бэкенда, фронтенда и шлюза, отправляет их
в Docker Hub и разворачивает проект на удалённом сервере.

## Автор

Алина Глушакова, [github.com/Aliases-s](https://github.com/Aliases-s)
EOF