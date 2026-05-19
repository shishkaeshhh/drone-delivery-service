# Frontend Prototype

Это статический прототип внешнего клиента для проверки Backend for Frontend endpoints. Он не является Django templates и не смешивается с backend-кодом.

Основной сценарий прототипа - внешний клиент сервиса доставки еды дронами. Экраны оператора и менеджера добавлены как внутренние рабочие роли компании, которые помогают выполнить заказ клиента.

## Запуск

Из корня проекта:

```bash
python3 -m http.server 5173 --directory frontend-prototype
```

Откройте:

```text
http://localhost:5173
```

Backend должен быть запущен отдельно:

```bash
docker compose up --build
docker compose exec web python scripts/populate_all.py
```

## Тестовые пользователи

- `client_1 / pass1234`
- `manager_1 / pass1234`
- `operator_1 / pass1234`

## Что проверяет прототип

- получение JWT через `/api/token/`;
- клиентский dashboard через `/api/bff/customer/dashboard/`;
- создание заказа через BFF;
- manager dashboard с проверкой группы `Managers`;
- operator control с проверкой группы `Operators`;
- health check `/api/bff/health/`.
