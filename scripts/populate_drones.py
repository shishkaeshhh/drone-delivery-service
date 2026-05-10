import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from delivery.models import Drone

def populate():
    drones_data = [
        {'name': 'Alpha-1', 'status': 'ready', 'battery_level': 100},
        {'name': 'Beta-2', 'status': 'in_flight', 'battery_level': 65},
        {'name': 'Gamma-3', 'status': 'charging', 'battery_level': 20},
        {'name': 'Delta-4', 'status': 'ready', 'battery_level': 98},
    ]

    for data in drones_data:
        Drone.objects.get_or_create(name=data['name'], defaults=data)
    
    print(f"Successfully populated {len(drones_data)} drones.")

if __name__ == '__main__':
    populate()
