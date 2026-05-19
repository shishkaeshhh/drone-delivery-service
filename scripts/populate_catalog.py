import os
import sys
import django

# Настройка окружения Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from delivery.models import CatalogItem

def populate():
    items_data = [
        # ВкусВилл
        {'store': 'vkusvill', 'name': 'Пицца Маргарита (ВкусВилл)', 'price': 550.00},
        {'store': 'vkusvill', 'name': 'Манго Египет', 'price': 350.00},
        {'store': 'vkusvill', 'name': 'Бургер с говядиной', 'price': 420.00},
        {'store': 'vkusvill', 'name': 'Свежевыжатый сок апельсиновый', 'price': 250.00},
        
        # Магнит
        {'store': 'magnit', 'name': 'Кока-Кола 1л', 'price': 110.00},
        {'store': 'magnit', 'name': 'Чипсы Lays Сыр', 'price': 135.00},
        {'store': 'magnit', 'name': 'Молоко Домик в Деревне 3.2%', 'price': 95.00},
        {'store': 'magnit', 'name': 'Хлеб нарезной', 'price': 45.00},

        # Пятерочка
        {'store': 'pyaterochka', 'name': 'Бананы 1кг', 'price': 120.00},
        {'store': 'pyaterochka', 'name': 'Пельмени Сибирская Коллекция', 'price': 490.00},
        {'store': 'pyaterochka', 'name': 'Шоколад Alpen Gold', 'price': 89.00},
        {'store': 'pyaterochka', 'name': 'Чай Greenfield', 'price': 150.00},

        # Лента
        {'store': 'lenta', 'name': 'Свиная шея 1кг', 'price': 550.00},
        {'store': 'lenta', 'name': 'Масло сливочное', 'price': 180.00},
        {'store': 'lenta', 'name': 'Яблоки сезонные 1кг', 'price': 110.00},
        {'store': 'lenta', 'name': 'Сыр Гауда 200г', 'price': 220.00},
    ]

    count = 0
    for data in items_data:
        # get_or_create чтобы не дублировать записи при повторном запуске
        obj, created = CatalogItem.objects.get_or_create(
            store=data['store'],
            name=data['name'],
            defaults={'price': data['price']}
        )
        if created:
            count += 1
            
    print(f"Успешно добавлено {count} новых товаров в каталог (всего в базе: {CatalogItem.objects.count()}).")

if __name__ == '__main__':
    populate()
