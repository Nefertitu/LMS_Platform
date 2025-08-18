# LMS_platform 
'LMS_platform' - учебный проект создания платформы для онлайн-обучения или 
LMS-системы, в которой каждый желающий может размещать свои полезные 
материалы или курсы.

## Установка и запуск проекта через Docker Compose

1. Клонируйте репозиторий:
```
git clone https://github.com/Nefertitu/LMS_Platform
```
или
```
git clone git@github.com:Nefertitu/LMS_Platform.git
```

```
cd LMS_platform
```

2. Скопируйте `.env.example` в `.env` и заполните переменные окружения:
   ```
   cp .env.sample .env
   ```
   
2. Запустите проект:
    ```
    docker-compose build --no-cache
    docker-compose up -d
    ```
   
3. Проверьте работоспособность:

- Откройте в браузере: http://localhost:8000

- База данных: 
```
   docker-compose logs db

```
```
  docker-compose exec db psql -U your_user -d your_db
```

- Redis:
```
   docker-compose logs redis
```
```
   docker-compose exec redis redis-cli ping
```

- Celery: 
```
   docker-compose logs celery
```
```
   docker-compose exec celery celery -A config status

```


- Celery Beat: 
```
   docker-compose logs celery-beat
```

- Выполните миграции и создайте суперпользователя:
```
docker-compose exec web python manage.py migrate
```
```
docker-compose exec web python manage.py csu
```
- Откройте в браузере: http://localhost:8000/admin/