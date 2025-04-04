# api_yamdb

## Описание
API для сайта рецензий на произведения.
Эндпоинты:
- api/v1/jwt/ (POST): получаем, обновляем или проверяем токен.
- api/v1/posts/ (GET, POST): получаем список всех постов или создаём новый пост.
- api/v1/posts/{post_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем пост с идентификатором post_id.
- api/v1/groups/ (GET): получаем список всех групп.
- api/v1/groups/{group_id}/ (GET): получаем информацию о группе с идентификатором group_id.
- api/v1/posts/{post_id}/comments/  (GET, POST): получаем список всех комментариев поста с идентификатором post_id или создаём новый комментарий для поста с идентификатором post_id
- api/v1/posts/{post_id}/comments/{comment_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем комментарий с идентификатором comment_id в посте с идентификатором post_id.
- api/v1/follow/ (GET, POST): получаем список подписок текущего пользователя или подписываемся на пользователя, переданного в запросе
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
Для получения списка всех постов направьте на эндпоинт `api/v1/posts/` GET запрос. При указании параметров limit и offset выдача будет работать с пагинацией.

Пример ответа
```
{
  "count": 123,
  "next": "http://api.example.org/accounts/?offset=400&limit=100",
  "previous": "http://api.example.org/accounts/?offset=200&limit=100",
  "results": [
    {
      "id": 0,
      "author": "string",
      "text": "string",
      "pub_date": "2021-10-14T20:41:29.648Z",
      "image": "string",
      "group": 0
    }
  ]
}
```
Когда вы запустите проект, по адресу `http://127.0.0.1:8000/redoc/` будет доступна полная документация для API Yatube с подробным описанием всех эндпоинтов