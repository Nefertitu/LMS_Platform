# LMS_platform 
'LMS_platform' - учебный проект создания платформы для онлайн-обучения или 
LMS-системы, в которой каждый желающий может размещать свои полезные 
материалы или курсы.

## Локальная установка и запуск проекта через Docker Compose

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
   
3. Проверьте работоспособность (проверка логов):

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

##  Автоматический деплой на сервер через GitHub Actions

При push в ветку `development` автоматически запускается CI/CD pipeline который:

✅ Тестирует код
✅ Собирает Docker образы  
✅ Деплоит на сервер
✅ Применяет миграции
✅ Собирает статические файлы
✅ Перезапускает сервисы

*Подробнее в [.github/workflows/ci.yml](.github/workflows/ci.yml)*


1. Форкните репозиторий
Перейдите на https://github.com/Nefertitu/LMS_Platform и нажмите "Fork"

2. Настройте сервер (Docker + Git)
```
ssh your_username@your_server_ip
```

3. Установите Docker и Git:
```
sudo apt update && sudo apt install docker.io docker-compose-plugin git -y
sudo usermod -aG docker $USER
newgrp docker
```
4. Настройте секреты в GitHub:
* В вашем форкнутом репозитории перейдите в Settings → Secrets → Actions
* Добавьте следующие секреты:
- DJANGO_SECRET_KEY - секретный ключ Django, можно сгенерировать: openssl rand -base64 32
- DOCKER_HUB_TOKEN - Токен из Docker Hub account settings
- DOCKER_HUB_USERNAME - Username из Docker Hub account settings
- SSH_USER - имя пользователя на сервере
- SERVER_IP - IP-адрес вашего сервера
- SSH_KEY - приватный SSH ключ
- POSTGRES_USER - postgres (или ваше значение)
- POSTGRES_PASSWORD - ваш_пароль
- POSTGRES_DB - lms_platform
- POSTGRES_PORT - 5432
- POSTGRES_SUPERUSER_PASSWORD - postgres

4. Проверка работоспособности:
* После деплоя проверьте:
- Статус контейнеров
```
docker-compose ps
```
- Логи приложения
```
docker-compose logs web
```
- Проверьте API
```
curl http://your-server-ip/api/courses/
```
7. Доступ к админке:

* Для первого входа создайте суперпользователя:
```
docker-compose exec web python manage.py csu
```
* Откройте в браузере: http://your-server-ip/admin/