# Диаграммы для проекта

Диаграммы можно построить в Mermaid, draw.io, PlantUML или diagrams.net. Для пояснительной записки лучше использовать 4 диаграммы:

- диаграмма вариантов использования;
- контейнерная диаграмма;
- sequence diagram создания заказа;
- ER-диаграмма.

## 1. Диаграмма вариантов использования

Что показывает:

- внешний клиент создает заказ и смотрит миссии;
- оператор контролирует доставку;
- менеджер смотрит метрики.

```mermaid
flowchart LR
    Customer["Внешний клиент"] --> Login["Авторизация"]
    Customer --> Catalog["Просмотр каталога еды"]
    Customer --> CreateOrder["Создание заказа"]
    Customer --> TrackOrders["Просмотр своих миссий"]

    Operator["Оператор компании"] --> OperatorLogin["Авторизация"]
    Operator --> NewMissions["Просмотр новых миссий"]
    Operator --> ReadyDrones["Просмотр готовых дронов"]
    Operator --> Telemetry["Просмотр телеметрии"]

    Manager["Менеджер компании"] --> ManagerLogin["Авторизация"]
    Manager --> Metrics["Просмотр метрик"]
    Manager --> MissionList["Просмотр миссий"]
```

Как объяснить:

```text
Главный актор системы - внешний клиент. Он использует сервис для заказа еды. Оператор и менеджер являются внутренними акторами компании и обеспечивают выполнение заказа.
```

## 2. Контейнерная диаграмма

Что показывает:

- frontend prototype;
- BFF;
- Django-приложения;
- PostgreSQL;
- Redis.

```mermaid
flowchart LR
    Client["Frontend prototype / Web-Mobile client"] --> BFF["Django BFF API"]
    BFF --> Delivery["delivery app"]
    BFF --> Telemetry["telemetry app"]
    BFF --> Accounts["accounts app"]
    Delivery --> DB[("PostgreSQL")]
    Telemetry --> DB
    Accounts --> DB
    Telemetry --> Redis[("Redis cache")]
```

Как объяснить:

```text
Frontend не обращается напрямую к отдельным доменным приложениям. Он использует BFF API, который собирает данные под конкретный экран.
```

## 3. Sequence diagram создания заказа

Что показывает:

- клиент отправляет заказ;
- BFF проверяет каталог;
- создается миссия доставки.

```mermaid
sequenceDiagram
    actor Customer as Внешний клиент
    participant UI as Frontend prototype
    participant BFF as BFF API
    participant Catalog as CatalogItem
    participant Mission as DeliveryMission
    participant DB as PostgreSQL

    Customer->>UI: Выбирает еду и адрес
    UI->>BFF: POST /api/bff/customer/dashboard/
    BFF->>Catalog: Проверить item_id или store/name
    Catalog-->>BFF: Еда найдена
    BFF->>Mission: Создать миссию доставки
    Mission->>DB: INSERT DeliveryMission
    DB-->>Mission: id миссии
    Mission-->>BFF: Данные миссии
    BFF-->>UI: 201 Created
```

Как объяснить:

```text
BFF не сохраняет произвольный заказ. Каждая позиция проверяется по каталогу еды, после чего заказ сохраняется в нормализованном виде.
```

## 4. Диаграмма ролей и доступа

Что показывает:

- клиент может работать только со своим dashboard;
- менеджер имеет доступ к manager dashboard;
- оператор имеет доступ к operator control.

```mermaid
flowchart TD
    User["JWT user"] --> CustomerEndpoint["Customer BFF endpoint"]
    User --> ManagerCheck{"Group Managers?"}
    User --> OperatorCheck{"Group Operators?"}

    ManagerCheck -->|yes| ManagerEndpoint["Manager dashboard"]
    ManagerCheck -->|no| ForbiddenManager["403 Forbidden"]

    OperatorCheck -->|yes| OperatorEndpoint["Operator control"]
    OperatorCheck -->|no| ForbiddenOperator["403 Forbidden"]
```

Как объяснить:

```text
JWT подтверждает личность пользователя, а группы Django ограничивают доступ к внутренним функциям оператора и менеджера.
```

## 5. ER-диаграмма

Что показывает:

- пользователь создает миссии;
- дрон назначается на миссию;
- дрон отправляет телеметрию;
- каталог содержит еду.

```mermaid
erDiagram
    CustomUser ||--o{ DeliveryMission : creates
    Drone ||--o{ DeliveryMission : assigned_to
    Drone ||--o{ Telemetry : sends

    CustomUser {
        int id
        string username
        string phone
    }

    CatalogItem {
        int id
        string store
        string name
        decimal price
    }

    DeliveryMission {
        int id
        int customer_id
        int drone_id
        string delivery_address
        json order_content
        string status
        datetime created_at
        datetime updated_at
    }

    Drone {
        int id
        string serial_number
        string model_name
        int battery_level
        string status
    }

    Telemetry {
        int id
        int drone_id
        float latitude
        float longitude
        float altitude
        datetime timestamp
    }
```

Как объяснить:

```text
Связь DeliveryMission с CatalogItem реализована через JSON order_content, потому что заказ хранит снимок цены и названия еды на момент оформления.
```

## 6. Как построить диаграммы в diagrams.net

1. Откройте `https://app.diagrams.net/`.
2. Выберите `Device` или `Google Drive`.
3. Создайте новую диаграмму.
4. Для контейнерной диаграммы используйте прямоугольники:
   - Frontend prototype;
   - Django BFF API;
   - delivery app;
   - telemetry app;
   - accounts app;
   - PostgreSQL;
   - Redis.
5. Соедините стрелками направление запросов.
6. Для ER-диаграммы используйте сущности как таблицы.
7. Для sequence diagram проще использовать Mermaid, затем экспортировать картинку.

## 7. Как вставить Mermaid в Markdown

В Markdown используйте блок:

````text
```mermaid
flowchart LR
    A --> B
```
````

GitHub умеет показывать Mermaid прямо в README и `.md` файлах.
