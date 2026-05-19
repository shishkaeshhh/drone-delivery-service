# Подробная инструкция деплоя на облачный сервер через GitHub Actions

## 1. Что будет в результате

После выполнения инструкции проект будет работать на облачном сервере:

- backend Django будет запущен в Docker контейнере;
- PostgreSQL будет хранить данные;
- Redis будет использоваться как cache backend;
- GitHub Actions будет автоматически запускать тесты и деплоить проект при push в ветку `main`;
- API будет доступен по IP или домену сервера;
- frontend prototype можно будет использовать локально или разместить отдельно как статические файлы.

## 2. Общая схема деплоя

```text
Developer laptop
  -> git push main
  -> GitHub Actions
  -> run tests
  -> SSH to cloud server
  -> git fetch/reset
  -> docker compose build
  -> docker compose up -d
  -> migrate
  -> collectstatic
  -> smoke tests
```

## 3. Что нужно подготовить

Нужны:

- аккаунт GitHub;
- репозиторий с проектом;
- облачный сервер Ubuntu 22.04 или Ubuntu 24.04;
- SSH-доступ к серверу;
- установленный Docker и Docker Compose plugin;
- GitHub Secrets для подключения к серверу.

Подойдет любой VPS/cloud server:

- Timeweb Cloud;
- Selectel;
- Yandex Cloud;
- VK Cloud;
- DigitalOcean;
- Hetzner;
- любой Ubuntu VPS.

## 4. Создание облачного сервера

При создании сервера выберите:

- OS: Ubuntu 22.04 LTS или Ubuntu 24.04 LTS;
- CPU: 1-2 vCPU для учебного проекта;
- RAM: 2 GB или больше;
- Disk: 20 GB или больше;
- Network: публичный IPv4;
- SSH key: добавьте публичный SSH-ключ.

После создания сервера сохраните:

- IP адрес сервера;
- имя пользователя, обычно `ubuntu` или `root`;
- путь к SSH ключу на локальном компьютере.

Проверка подключения:

```bash
ssh ubuntu@SERVER_IP
```

Если сервер использует пользователя `root`:

```bash
ssh root@SERVER_IP
```

## 5. Создание отдельного пользователя для деплоя

Если вы зашли под `root`, лучше создать отдельного пользователя:

```bash
adduser deploy
usermod -aG sudo deploy
```

Добавьте SSH ключ:

```bash
mkdir -p /home/deploy/.ssh
nano /home/deploy/.ssh/authorized_keys
```

Вставьте публичный ключ, затем:

```bash
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

Проверьте вход:

```bash
ssh deploy@SERVER_IP
```

Дальше в инструкции пользователь называется `deploy`. Если вы используете `ubuntu`, подставляйте `ubuntu`.

## 6. Установка Git, Docker и Docker Compose

На сервере:

```bash
sudo apt update
sudo apt install -y git ca-certificates curl gnupg
```

Установите Docker из репозитория Ubuntu:

```bash
sudo apt install -y docker.io docker-compose-plugin
```

Добавьте пользователя в группу `docker`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Проверка:

```bash
docker --version
docker compose version
docker ps
```

Для чего это нужно:

- `git` нужен, чтобы сервер мог получать код из GitHub;
- `docker.io` нужен для запуска контейнеров;
- `docker-compose-plugin` нужен для команды `docker compose`;
- группа `docker` позволяет запускать Docker без `sudo`.

## 7. Подготовка директории проекта на сервере

Создайте директорию:

```bash
sudo mkdir -p /opt/drone-platform
sudo chown -R $USER:$USER /opt/drone-platform
cd /opt/drone-platform
```

Склонируйте репозиторий:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git .
```

Проверьте файлы:

```bash
ls -la
```

В директории должны быть:

- `manage.py`;
- `Dockerfile`;
- `docker-compose.yml`;
- `requirements.txt`;
- папки `accounts`, `delivery`, `telemetry`, `bff`.

## 8. Создание production `.env`

В корне проекта на сервере создайте `.env`:

```bash
nano /opt/drone-platform/.env
```

Пример:

```env
SECRET_KEY=replace-this-with-long-random-secret
DEBUG=False
ALLOWED_HOSTS=SERVER_IP,your-domain.com
CORS_ALLOW_ALL_ORIGINS=True

DB_NAME=drone_db
DB_USER=drone_user
DB_PASSWORD=very_strong_database_password
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
```

Что означает каждая переменная:

- `SECRET_KEY` - секрет Django. Нельзя публиковать в GitHub.
- `DEBUG=False` - production режим. Ошибки не показываются пользователям.
- `ALLOWED_HOSTS` - IP или домен, с которого разрешено открывать backend.
- `CORS_ALLOW_ALL_ORIGINS=True` - для учебного прототипа разрешает запросы с frontend prototype. Для реального production лучше ограничить CORS конкретным доменом.
- `DB_NAME` - имя базы PostgreSQL.
- `DB_USER` - пользователь PostgreSQL.
- `DB_PASSWORD` - пароль PostgreSQL.
- `DB_HOST=db` - имя Docker service PostgreSQL из `docker-compose.yml`.
- `REDIS_URL` - адрес Redis внутри Docker Compose сети.

Сгенерировать `SECRET_KEY` можно локально:

```bash
python3 - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

Если Django локально не установлен, можно сгенерировать обычный длинный случайный пароль:

```bash
openssl rand -base64 48
```

## 9. Первый ручной запуск на сервере

Первый запуск лучше сделать вручную, чтобы убедиться, что сервер настроен правильно.

```bash
cd /opt/drone-platform
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Применить миграции:

```bash
docker compose exec web python manage.py migrate
```

Заполнить демо-данные:

```bash
docker compose exec web python scripts/populate_all.py
```

Собрать static:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Проверить тесты:

```bash
docker compose exec web python manage.py test
```

Проверить health endpoint:

```bash
curl http://SERVER_IP:8000/api/bff/health/
```

Ожидаемый ответ:

```json
{"status":"ok","service":"drone-delivery-bff"}
```

## 10. Настройка GitHub Secrets

В GitHub:

1. Откройте репозиторий.
2. Перейдите в `Settings`.
3. Откройте `Secrets and variables`.
4. Откройте `Actions`.
5. Нажмите `New repository secret`.

Добавьте secrets:

| Secret | Значение | Для чего нужен |
|---|---|---|
| `SERVER_HOST` | IP или домен сервера | GitHub Actions будет подключаться к этому серверу |
| `SERVER_USER` | `deploy` или `ubuntu` | Пользователь SSH |
| `SERVER_SSH_KEY` | приватный SSH ключ | Ключ для подключения без пароля |
| `SERVER_SSH_PORT` | `22` | SSH порт |
| `PROJECT_PATH` | `/opt/drone-platform` | Где лежит проект на сервере |

Важно:

- в `SERVER_SSH_KEY` вставляется приватный ключ целиком;
- публичная часть этого ключа должна лежать на сервере в `~/.ssh/authorized_keys`;
- приватный ключ нельзя коммитить в репозиторий.

Проверить приватный ключ локально:

```bash
cat ~/.ssh/id_ed25519
```

Пример начинается так:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
```

И заканчивается так:

```text
-----END OPENSSH PRIVATE KEY-----
```

## 11. Как работает `.github/workflows/deploy.yml`

Workflow состоит из двух jobs:

- `test`;
- `deploy`.

### Job `test`

Этот job запускается в GitHub Actions перед деплоем.

Что он делает:

1. Поднимает PostgreSQL service.
2. Поднимает Redis service.
3. Устанавливает Python 3.10.
4. Устанавливает зависимости из `requirements.txt`.
5. Проверяет миграции:

```bash
python manage.py makemigrations --check --dry-run
```

Эта команда нужна, чтобы убедиться: модели и миграции синхронизированы.

6. Запускает тесты:

```bash
python manage.py test
```

Если тесты падают, деплой не выполняется.

### Job `deploy`

Этот job запускается только после успешного `test`.

Что он делает:

1. Подключается к серверу по SSH.
2. Переходит в `PROJECT_PATH`.
3. Забирает свежий код из `main`.
4. Пересобирает Docker images.
5. Запускает контейнеры.
6. Применяет миграции.
7. Собирает static.
8. Запускает тесты на сервере.

## 12. Как выполнить деплой

После настройки сервера и GitHub Secrets:

```bash
git add .
git commit -m "Prepare BFF deployment"
git push origin main
```

GitHub Actions автоматически запустит workflow.

Проверить выполнение:

1. Откройте GitHub repository.
2. Перейдите во вкладку `Actions`.
3. Выберите workflow `Test and Deploy Drone Platform`.
4. Откройте последний запуск.
5. Убедитесь, что `test` и `deploy` зеленые.

## 13. Проверка после деплоя

На локальном компьютере:

```bash
curl http://SERVER_IP:8000/api/bff/health/
```

Получить JWT:

```bash
curl -X POST http://SERVER_IP:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"client_1","password":"pass1234"}'
```

Проверить клиентский dashboard:

```bash
curl http://SERVER_IP:8000/api/bff/customer/dashboard/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

Проверить operator endpoint:

```bash
curl http://SERVER_IP:8000/api/bff/operator/control/ \
  -H "Authorization: Bearer OPERATOR_ACCESS_TOKEN"
```

## 14. Настройка Nginx как reverse proxy

Без Nginx API доступно на порту `8000`:

```text
http://SERVER_IP:8000
```

Для более правильного production-вида можно поставить Nginx:

```bash
sudo apt install -y nginx
```

Создайте конфиг:

```bash
sudo nano /etc/nginx/sites-available/drone-platform
```

Вставьте:

```nginx
server {
    listen 80;
    server_name SERVER_IP your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте:

```bash
sudo ln -s /etc/nginx/sites-available/drone-platform /etc/nginx/sites-enabled/drone-platform
sudo nginx -t
sudo systemctl reload nginx
```

Теперь API будет доступно:

```text
http://SERVER_IP/api/bff/health/
```

Если используете домен, замените `SERVER_IP` на домен.

## 15. HTTPS через Let's Encrypt

Если есть домен:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Проверка автообновления:

```bash
sudo certbot renew --dry-run
```

## 16. Полезные команды сопровождения

Посмотреть контейнеры:

```bash
docker compose ps
```

Посмотреть логи backend:

```bash
docker compose logs -f web
```

Посмотреть логи PostgreSQL:

```bash
docker compose logs -f db
```

Перезапустить сервисы:

```bash
docker compose restart
```

Остановить проект:

```bash
docker compose down
```

Пересобрать:

```bash
docker compose build --pull
docker compose up -d
```

Повторно заполнить демо-данные:

```bash
docker compose exec web python scripts/populate_all.py
```

## 17. Что делать, если деплой упал

### Ошибка SSH

Проверьте:

- `SERVER_HOST`;
- `SERVER_USER`;
- `SERVER_SSH_PORT`;
- что публичный ключ есть в `authorized_keys`;
- что приватный ключ полностью вставлен в `SERVER_SSH_KEY`.

### Ошибка Docker permission denied

На сервере:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Ошибка ALLOWED_HOSTS

В `.env` добавьте IP или домен:

```env
ALLOWED_HOSTS=SERVER_IP,your-domain.com
```

Перезапустите:

```bash
docker compose up -d
```

### Ошибка базы данных

Проверьте:

```bash
docker compose ps
docker compose logs db
docker compose logs web
```

Пароль `DB_PASSWORD` должен совпадать в PostgreSQL service и web service. В текущем `docker-compose.yml` это берется из одной переменной.

## 18. Как объяснить деплой в работе

Формулировка:

```text
Деплой реализован через GitHub Actions. При отправке изменений в ветку main CI/CD pipeline поднимает сервисы PostgreSQL и Redis, устанавливает зависимости, проверяет миграции и запускает тесты. Только после успешных тестов workflow подключается к облачному серверу по SSH, обновляет код проекта, пересобирает Docker Compose сервисы, применяет миграции и запускает приложение. Такой подход снижает риск попадания неработающего кода на сервер.
```
