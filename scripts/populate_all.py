import os
import sys

import django


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group

from accounts.models import CustomUser
from delivery.models import CatalogItem, DeliveryMission, Drone
from telemetry.models import Telemetry


FOOD_CATALOG = [
    {'store': 'vkusvill', 'name': 'Пицца Маргарита', 'price': 550.00},
    {'store': 'vkusvill', 'name': 'Боул с курицей и киноа', 'price': 390.00},
    {'store': 'vkusvill', 'name': 'Бургер с говядиной', 'price': 420.00},
    {'store': 'vkusvill', 'name': 'Свежевыжатый апельсиновый сок', 'price': 250.00},
    {'store': 'magnit', 'name': 'Кока-Кола 1л', 'price': 110.00},
    {'store': 'magnit', 'name': 'Чипсы Lays Сыр', 'price': 135.00},
    {'store': 'magnit', 'name': 'Салат Цезарь готовый', 'price': 230.00},
    {'store': 'magnit', 'name': 'Сэндвич с индейкой', 'price': 180.00},
    {'store': 'pyaterochka', 'name': 'Бананы 1кг', 'price': 120.00},
    {'store': 'pyaterochka', 'name': 'Пельмени Сибирская Коллекция', 'price': 490.00},
    {'store': 'pyaterochka', 'name': 'Шоколад Alpen Gold', 'price': 89.00},
    {'store': 'pyaterochka', 'name': 'Чай Greenfield', 'price': 150.00},
    {'store': 'lenta', 'name': 'Свиная шея 1кг', 'price': 550.00},
    {'store': 'lenta', 'name': 'Сыр Гауда 200г', 'price': 220.00},
    {'store': 'lenta', 'name': 'Яблоки сезонные 1кг', 'price': 110.00},
    {'store': 'lenta', 'name': 'Паста карбонара готовая', 'price': 310.00},
    {'store': 'depo', 'name': 'Фо Бо', 'price': 450.00},
    {'store': 'depo', 'name': 'Поке с лососем', 'price': 650.00},
    {'store': 'depo', 'name': 'Чизбургер', 'price': 480.00},
    {'store': 'depo', 'name': 'Лимонад маракуйя', 'price': 260.00},
    {'store': 'syrovarnya', 'name': 'Сыр Буррата с томатами', 'price': 950.00},
    {'store': 'syrovarnya', 'name': 'Пицца 4 сыра', 'price': 1100.00},
    {'store': 'syrovarnya', 'name': 'Паппарделле с белыми грибами', 'price': 850.00},
    {'store': 'white_rabbit', 'name': 'Борщ с говядиной', 'price': 980.00},
    {'store': 'white_rabbit', 'name': 'Краб с соусом из икры', 'price': 2500.00},
    {'store': 'white_rabbit', 'name': 'Медовик со сметанным мороженым', 'price': 750.00},
    {'store': 'pushkin', 'name': 'Пельмени с телятиной', 'price': 1200.00},
    {'store': 'pushkin', 'name': 'Блины с красной икрой', 'price': 1500.00},
    {'store': 'pushkin', 'name': 'Пожарская котлета с пюре', 'price': 1450.00},
]


def upsert_user(username, password, phone, group=None):
    user, _ = CustomUser.objects.get_or_create(username=username, defaults={'phone': phone})
    user.phone = phone
    user.set_password(password)
    user.save()
    if group:
        user.groups.add(group)
    return user


def upsert_catalog():
    items = {}
    for data in FOOD_CATALOG:
        item, _ = CatalogItem.objects.update_or_create(
            store=data['store'],
            name=data['name'],
            defaults={'price': data['price']},
        )
        items[(item.store, item.name)] = item
    return items


def order_line(catalog_items, store, name, quantity):
    item = catalog_items[(store, name)]
    unit_price = float(item.price)
    return {
        'item_id': item.id,
        'store': item.store,
        'store_name': item.get_store_display(),
        'name': item.name,
        'quantity': quantity,
        'unit_price': unit_price,
        'line_total': round(unit_price * quantity, 2),
    }


def upsert_mission(customer, address, status, order_content, drone=None):
    mission, _ = DeliveryMission.objects.update_or_create(
        customer=customer,
        delivery_address=address,
        defaults={
            'drone': drone,
            'status': status,
            'order_content': order_content,
        },
    )
    return mission


def populate():
    print('Начинаем заполнение проекта демо-данными...')

    managers_group, _ = Group.objects.get_or_create(name='Managers')
    operators_group, _ = Group.objects.get_or_create(name='Operators')

    manager = upsert_user('manager_1', 'pass1234', '+79990001122', managers_group)
    operator = upsert_user('operator_1', 'pass1234', '+79990001133', operators_group)
    client1 = upsert_user('client_1', 'pass1234', '+79990001144')
    client2 = upsert_user('client_2', 'pass1234', '+79990001155')
    client3 = upsert_user('client_3', 'pass1234', '+79990001166')

    drones_data = [
        {'serial_number': 'DRN-001', 'model_name': 'DJI Matrice 300 RTK', 'battery_level': 100, 'status': 'ready'},
        {'serial_number': 'DRN-002', 'model_name': 'SwellPro Fisherman FD1', 'battery_level': 85, 'status': 'flying'},
        {'serial_number': 'DRN-003', 'model_name': 'Yuneec H520', 'battery_level': 15, 'status': 'charging'},
        {'serial_number': 'DRN-004', 'model_name': 'Autel Evo II', 'battery_level': 95, 'status': 'ready'},
        {'serial_number': 'DRN-005', 'model_name': 'DJI FlyCart 30', 'battery_level': 72, 'status': 'flying'},
    ]
    drones = {}
    for data in drones_data:
        drone, _ = Drone.objects.update_or_create(
            serial_number=data['serial_number'],
            defaults=data,
        )
        drones[drone.serial_number] = drone

    catalog_items = upsert_catalog()

    # Recreate demo missions so the project contains only catalog-based food orders.
    demo_clients = [client1, client2, client3]
    Telemetry.objects.all().delete()
    DeliveryMission.objects.all().delete()

    upsert_mission(
        customer=client1,
        address='г. Москва, ул. Арбат, д. 10',
        status='new',
        order_content=[
            order_line(catalog_items, 'vkusvill', 'Бургер с говядиной', 2),
            order_line(catalog_items, 'vkusvill', 'Свежевыжатый апельсиновый сок', 2),
        ],
    )

    mission_in_progress = upsert_mission(
        customer=client2,
        address='г. Москва, Тверская, 15',
        status='in_progress',
        drone=drones['DRN-002'],
        order_content=[
            order_line(catalog_items, 'syrovarnya', 'Пицца 4 сыра', 1),
            order_line(catalog_items, 'syrovarnya', 'Паппарделле с белыми грибами', 1),
        ],
    )

    mission_restaurant = upsert_mission(
        customer=client3,
        address='г. Москва, Цветной бульвар, д. 2',
        status='in_progress',
        drone=drones['DRN-005'],
        order_content=[
            order_line(catalog_items, 'depo', 'Фо Бо', 2),
            order_line(catalog_items, 'depo', 'Лимонад маракуйя', 2),
        ],
    )

    upsert_mission(
        customer=client1,
        address='г. Москва, ул. Ленина, д. 5',
        status='completed',
        drone=drones['DRN-004'],
        order_content=[
            order_line(catalog_items, 'pushkin', 'Пельмени с телятиной', 1),
            order_line(catalog_items, 'pushkin', 'Блины с красной икрой', 1),
        ],
    )

    upsert_mission(
        customer=client2,
        address='г. Москва, Пресненская наб., д. 8',
        status='new',
        order_content=[
            order_line(catalog_items, 'magnit', 'Салат Цезарь готовый', 1),
            order_line(catalog_items, 'magnit', 'Сэндвич с индейкой', 2),
            order_line(catalog_items, 'magnit', 'Кока-Кола 1л', 1),
        ],
    )

    telemetry_points = [
        (mission_in_progress.drone, 55.7558, 37.6173, 120.5),
        (mission_in_progress.drone, 55.7581, 37.6240, 118.2),
        (mission_restaurant.drone, 55.7714, 37.6208, 104.0),
        (mission_restaurant.drone, 55.7770, 37.6315, 99.5),
    ]
    for drone, latitude, longitude, altitude in telemetry_points:
        Telemetry.objects.create(
            drone=drone,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
        )

    print(f'Пользователи готовы: {manager.username}, {operator.username}, client_1, client_2, client_3. Пароль: pass1234')
    print(f'Каталог еды заполнен: {CatalogItem.objects.count()} позиций.')
    print(f'Миссии доставки еды созданы: {DeliveryMission.objects.filter(customer__in=demo_clients).count()}.')
    print(f'Телеметрия создана: {Telemetry.objects.count()} записей.')
    print('Демо-данные готовы.')


if __name__ == '__main__':
    populate()
