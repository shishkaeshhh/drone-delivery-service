from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from delivery.models import CatalogItem, DeliveryMission, Drone

User = get_user_model()

class AuthenticationAndMissionTests(APITestCase):

    def setUp(self):
        self.managers = Group.objects.create(name='Managers')
        self.operators = Group.objects.create(name='Operators')

        self.manager = User.objects.create_user(
            username='manager_test',
            password='testpassword123',
        )
        self.manager.groups.add(self.managers)

        self.operator = User.objects.create_user(
            username='operator_test',
            password='testpassword123',
        )
        self.operator.groups.add(self.operators)

        self.customer = User.objects.create_user(
            username='customer_test',
            password='testpassword123',
        )

        self.token_url = reverse('token_obtain_pair')
        self.missions_url = '/api/delivery/missions/'
        self.catalog_item = CatalogItem.objects.create(
            store='vkusvill',
            name='Бургер с говядиной',
            price=420,
        )

    def get_token(self, username, password):
        response = self.client.post(self.token_url, {
            'username': username,
            'password': password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def test_create_mission_with_token(self):
        token = self.get_token('customer_test', 'testpassword123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.post(self.missions_url, {
            'delivery_address': 'Moscow, Test street, 1',
            'order_content': [{'name': 'Pizza', 'quantity': 1, 'price': 500}]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryMission.objects.count(), 1)
        self.assertEqual(DeliveryMission.objects.get().customer, self.customer)

    def test_access_without_token_fails(self):
        response = self.client.post(self.missions_url, {
            'delivery_address': 'Moscow, Test street, 1',
            'order_content': [{'name': 'Pizza', 'quantity': 1, 'price': 500}]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(DeliveryMission.objects.count(), 0)

    def test_list_missions_with_operator_token(self):
        DeliveryMission.objects.create(customer=self.customer, status='new')

        token = self.get_token('operator_test', 'testpassword123')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.missions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class BFFEndpointTests(APITestCase):
    def setUp(self):
        managers = Group.objects.create(name='Managers')
        operators = Group.objects.create(name='Operators')
        self.customer = User.objects.create_user(username='customer_bff', password='testpassword123', phone='+70000000001')
        self.manager = User.objects.create_user(username='manager_bff', password='testpassword123')
        self.operator = User.objects.create_user(username='operator_bff', password='testpassword123')
        self.manager.groups.add(managers)
        self.operator.groups.add(operators)
        self.drone = Drone.objects.create(serial_number='DRN-TEST-1', model_name='Test Drone', status='ready')
        self.catalog_item = CatalogItem.objects.create(
            store='vkusvill',
            name='Бургер с говядиной',
            price=420,
        )
        DeliveryMission.objects.create(customer=self.customer, delivery_address='Moscow', status='new')

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_customer_dashboard_contains_profile_and_missions(self):
        self.authenticate(self.customer)

        response = self.client.get('/api/bff/customer/dashboard/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['username'], 'customer_bff')
        self.assertEqual(len(response.data['missions']), 1)

    def test_customer_can_create_order_through_bff(self):
        self.authenticate(self.customer)

        response = self.client.post('/api/bff/customer/dashboard/', {
            'delivery_address': 'Moscow, New address',
            'order_content': [{'item_id': self.catalog_item.id, 'quantity': 2}]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryMission.objects.filter(customer=self.customer).count(), 2)
        created = DeliveryMission.objects.latest('id')
        self.assertEqual(created.order_content[0]['name'], 'Бургер с говядиной')
        self.assertEqual(created.order_content[0]['store'], 'vkusvill')

    def test_customer_order_must_use_catalog_food_item(self):
        self.authenticate(self.customer)

        response = self.client.post('/api/bff/customer/dashboard/', {
            'delivery_address': 'Moscow, New address',
            'order_content': [{'name': 'Nonexistent Item', 'quantity': 1}]
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_dashboard_requires_manager_group(self):
        self.authenticate(self.customer)
        forbidden = self.client.get('/api/bff/manager/dashboard/')
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.authenticate(self.manager)
        allowed = self.client.get('/api/bff/manager/dashboard/')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', allowed.data)

    def test_operator_control_returns_new_missions_and_ready_drones(self):
        self.authenticate(self.operator)

        response = self.client.get('/api/bff/operator/control/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['new_missions']), 1)
        self.assertEqual(len(response.data['ready_drones']), 1)
