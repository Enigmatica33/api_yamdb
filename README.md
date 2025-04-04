# api_yamdb
Проект YaMDb собирает отзывы пользователей на различные произведения искусства.
## Описание
Эндпоинты:
- api/v1/auth/signup/ (POST): регистрация нового пользователя
- api/v1/auth/token/ (POST): получить токен.
- api/v1/auth/users/ (GET, POST): Получить список всех пользователей или добавить нового. Права доступа: Администратор
- api/v1/auth/users/{username}/ (GET, PATCH, DELETE): Получение, изменение данных и удаление пользователя по username. Права доступа: Администратор
- api/v1/users/me/ (GET, PATCH): Получить и изменить данные своей учетной записи
- api/v1/titles/ (GET, POST): Получить список всех произведений или создаём новое произведение.
- api/v1/titles/{title_id}/ (GET, PATCH, DELETE): получаем, редактируем или удаляем произведение с идентификатором title_id.
- api/v1/categories/ (GET, POST): Получить список всех категорий(типов) произведений или добавить новую.
- api/v1/categories/{slug}/ (DELETE): Удалить категорию с идентификатором slug.
- api/v1/genres/ (GET, POST): Получить список всех жанров произведений или добавить новый.
- api/v1/genres/{slug}/ (DELETE): Удалить жанр с идентификатором slug.
- api/v1/titles/{title_id}/reviews/  (GET, POST): Получить список всех отзывов произведения с идентификатором title_id или добавить новый отзыв о произведении с идентификатором title_id
- api/v1/titles/{title_id}/reviews/{review_id}/ (GET, PATCH, DELETE): Получить, обновить или удалить отзыв по id для указанного произведения
- api/v1/titles/{title_id}/reviews/{review_id}/comments/ (GET, POST): Получить список всех комментариев к отзыву по id или добавить новый комменатрий для отзыва
- api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id} (GET, PATCH, DELETE) Получить комментарий для отзыва по id, частично обновить или добавить новый

***

## Используемые технологии 
API написан на Python с использованием библиотеки DjangoRESTframework.
Аутентификация настроена c помощью библиотек Djoser и Simple JWT.
***

## Как запустить проект
Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Примеры запросов

Для получения списка всех произведений направьте на эндпоинт `api/v1/titles/` GET запрос. При указании параметров limit и offset выдача будет работать с пагинацией.

Пример ответа
```
{
"id": 0,
"name": "string",
"year": 0,
"rating": 0,
"description": "string",
"genre": [
{}
],
"category": {
"name": "string",
"slug": "^-$"
}
}
```
Когда вы запустите проект, по адресу `http://127.0.0.1:8000/redoc/` будет доступна полная документация для API YaMDB с подробным описанием всех эндпоинтов