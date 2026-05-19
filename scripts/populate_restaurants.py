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
        # Фудмолл Депо
        {'store': 'depo', 'name': 'Фо Бо (Bo)', 'price': 450.00},
        {'store': 'depo', 'name': 'Поке с лососем (Soul in the Bowl)', 'price': 650.00},
        {'store': 'depo', 'name': 'Стейк Рибай (Meat Dealers)', 'price': 1800.00},
        {'store': 'depo', 'name': 'Чизбургер (Corner Burger)', 'price': 480.00},
        
        # Сыроварня
        {'store': 'syrovarnya', 'name': 'Сыр Буррата с томатами', 'price': 950.00},
        {'store': 'syrovarnya', 'name': 'Пицца 4 сыра из дровяной печи', 'price': 1100.00},
        {'store': 'syrovarnya', 'name': 'Паппарделле с белыми грибами', 'price': 850.00},
        {'store': 'syrovarnya', 'name': 'Домашний лимонад маракуйя', 'price': 450.00},

        # White Rabbit
        {'store': 'white_rabbit', 'name': 'Борщ с жареными карасями', 'price': 980.00},
        {'store': 'white_rabbit', 'name': 'Краб с соусом из икры', 'price': 2500.00},
        {'store': 'white_rabbit', 'name': 'Медовик со сметанным мороженым', 'price': 750.00},
        {'store': 'white_rabbit', 'name': 'Сет "Эволюция"', 'price': 15000.00},

        # Кафе Пушкинъ
        {'store': 'pushkin', 'name': 'Пельмени с телятиной в горшочке', 'price': 1200.00},
        {'store': 'pushkin', 'name': 'Блины с красной икрой', 'price': 1500.00},
        {'store': 'pushkin', 'name': 'Пожарская котлета с пюре', 'price': 1450.00},
        {'store': 'pushkin', 'name': 'Десерт "Клубника Романова"', 'price': 950.00},
    ]

    count = 0
    for data in items_data:
        obj, created = CatalogItem.objects.get_or_create(
            store=data['store'],
            name=data['name'],
            defaults={'price': data['price']}
        )
        if created:
            count += 1
            
    print(f"Успешно добавлено {count} блюд из московских ресторанов (всего в базе: {CatalogItem.objects.count()}).")

if __name__ == '__main__':
    populate()
