# Проверка проекта через Postman

## 1. Подготовка

Запустите backend:

```bash
docker compose up --build
```

В другом терминале заполните данные:

```bash
docker compose exec web python scripts/populate_all.py
```

Проверьте health endpoint:

```bash
curl http://localhost:8000/api/bff/health/
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "drone-delivery-bff"
}
```

## 2. Импорт коллекции

В Postman:

1. Нажмите `Import`.
2. Выберите файл `postman_collection.json`.
3. Откройте коллекцию `Drone Delivery Platform BFF`.

## 3. Переменные коллекции

В коллекции есть переменные:

- `base_url` - адрес backend;
- `access_token` - JWT клиента;
- `manager_token` - JWT менеджера;
- `operator_token` - JWT оператора.

Для локальной проверки:

```text
base_url = http://localhost:8000
```

Для сервера:

```text
base_url = http://SERVER_IP:8000
```

Если настроен Nginx:

```text
base_url = http://SERVER_IP
```

## 4. Тестовые пользователи

Скрипт `scripts/populate_all.py` создает пользователей:

| Пользователь | Пароль | Роль |
|---|---|---|
| `client_1` | `pass1234` | внешний клиент |
| `client_2` | `pass1234` | внешний клиент |
| `client_3` | `pass1234` | внешний клиент |
| `operator_1` | `pass1234` | оператор |
| `manager_1` | `pass1234` | менеджер |

## 5. Последовательность проверки

### Шаг 1. Health Check

Запрос:

```http
GET {{base_url}}/api/bff/health/
```

Ожидаемый статус:

```text
200 OK
```

Зачем проверять:

- подтверждает, что backend запущен;
- подтверждает, что URL указан правильно;
- подходит для smoke-test после деплоя.

### Шаг 2. Get Token

Запрос:

```http
POST {{base_url}}/api/token/
Content-Type: application/json
```

Body:

```json
{
  "username": "client_1",
  "password": "pass1234"
}
```

Ожидаемый статус:

```text
200 OK
```

Ожидаемые поля:

- `access`;
- `refresh`.

Коллекция автоматически сохранит `access` в `access_token`.

### Шаг 3. Customer Dashboard

Запрос:

```http
GET {{base_url}}/api/bff/customer/dashboard/
Authorization: Bearer {{access_token}}
```

Ожидаемый статус:

```text
200 OK
```

В ответе должны быть:

- `profile`;
- `stores`;
- `catalog_preview`;
- `missions`.

Зачем проверять:

- доказывает работу BFF для внешнего клиента;
- показывает каталог еды;
- показывает миссии клиента.

### Шаг 4. Create Customer Order

Запрос:

```http
POST {{base_url}}/api/bff/customer/dashboard/
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "delivery_address": "г. Москва, ул. Арбат, д. 10",
  "order_content": [
    {
      "store": "vkusvill",
      "name": "Бургер с говядиной",
      "quantity": 2
    }
  ]
}
```

Ожидаемый статус:

```text
201 Created
```

В ответе позиция заказа должна быть нормализована:

```json
{
  "item_id": 17,
  "store": "vkusvill",
  "store_name": "ВкусВилл",
  "name": "Бургер с говядиной",
  "quantity": 2,
  "unit_price": 420.0,
  "line_total": 840.0
}
```

Зачем проверять:

- подтверждает, что клиент не создает произвольный заказ;
- заказ состоит из еды из каталога;
- BFF проверяет предметную область.

### Шаг 5. Manager Token

Получите токен менеджера:

```json
{
  "username": "manager_1",
  "password": "pass1234"
}
```

Коллекция сохранит токен в `manager_token`.

### Шаг 6. Manager Dashboard

Запрос:

```http
GET {{base_url}}/api/bff/manager/dashboard/
Authorization: Bearer {{manager_token}}
```

Ожидаемый статус:

```text
200 OK
```

В ответе:

- `metrics`;
- `missions`.

Зачем проверять:

- подтверждает роль менеджера;
- показывает управленческий BFF endpoint.

### Шаг 7. Operator Token

Получите токен оператора:

```json
{
  "username": "operator_1",
  "password": "pass1234"
}
```

Коллекция сохранит токен в `operator_token`.

### Шаг 8. Operator Control

Запрос:

```http
GET {{base_url}}/api/bff/operator/control/
Authorization: Bearer {{operator_token}}
```

Ожидаемый статус:

```text
200 OK
```

В ответе:

- `new_missions`;
- `ready_drones`;
- `telemetry`.

Зачем проверять:

- подтверждает роль оператора;
- показывает операционный сценарий предметной области;
- оператор видит миссии, дроны и телеметрию.

## 6. Проверка ограничения доступа

Попробуйте открыть manager endpoint с токеном клиента:

```http
GET {{base_url}}/api/bff/manager/dashboard/
Authorization: Bearer {{access_token}}
```

Ожидаемый статус:

```text
403 Forbidden
```

Попробуйте открыть operator endpoint с токеном клиента:

```http
GET {{base_url}}/api/bff/operator/control/
Authorization: Bearer {{access_token}}
```

Ожидаемый статус:

```text
403 Forbidden
```

Это подтверждает, что роли разделены.

## 7. Проверка ошибочного заказа

Создайте заказ с несуществующей едой:

```json
{
  "delivery_address": "г. Москва, тест",
  "order_content": [
    {
      "name": "Несуществующая еда",
      "quantity": 1
    }
  ]
}
```

Ожидаемый статус:

```text
400 Bad Request
```

Это подтверждает, что заказ нельзя создать из произвольного текста.
