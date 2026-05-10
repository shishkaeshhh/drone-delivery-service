from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from delivery.models import DeliveryMission, Drone

User = get_user_model()

class AuthenticationAndMissionTests(APITestCase):

    def setUp(self):
        # Create a test manager
        self.manager = User.objects.create_user(
            username='manager_test',
            password='testpassword123',
            role='manager'
        )

        # Create a test operator
        self.operator = User.objects.create_user(
            username='operator_test',
            password='testpassword123',
            role='operator'
        )

        # Create a customer
        self.customer = User.objects.create_user(
            username='customer_test',
            password='testpassword123',
            role='client'
        )

        # Token URLs
        self.token_url = reverse('token_obtain_pair')
        
        # We assume there is a missions endpoint. We'll use the hardcoded URL if reverse fails.
        self.missions_url = '/api/delivery/missions/'

    def get_token(self, username, password):
        response = self.client.post(self.token_url, {
            'username': username,
            'password': password
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def test_create_mission_with_token(self):
        # Get token for manager
        token = self.get_token('manager_test', 'testpassword123')
        
        # Include token in headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        
        # Test creation of mission
        response = self.client.post(self.missions_url, {
            'customer': self.customer.id,
            'status': 'new'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryMission.objects.count(), 1)
        self.assertEqual(DeliveryMission.objects.get().customer, self.customer)

    def test_access_without_token_fails(self):
        # Try creating mission without token
        response = self.client.post(self.missions_url, {
            'customer': self.customer.id,
            'status': 'new'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(DeliveryMission.objects.count(), 0)

    def test_list_missions_with_operator_token(self):
        # Create a mission manually
        DeliveryMission.objects.create(customer=self.customer, status='new')

        # Get token for operator
        token = self.get_token('operator_test', 'testpassword123')
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.missions_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
