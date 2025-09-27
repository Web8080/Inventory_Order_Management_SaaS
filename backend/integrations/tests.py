from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
import json

from tenants.models import Tenant
from .models import Integration, IntegrationSync, IntegrationWebhook

User = get_user_model()


class IntegrationModelTest(TestCase):
    """Test Integration model"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
    
    def test_create_integration(self):
        """Test creating an integration"""
        integration = Integration.objects.create(
            tenant=self.tenant,
            name="Test Shopify Store",
            integration_type="shopify",
            status="active",
            api_key="test_key",
            config={"shop_domain": "test-shop"}
        )
        
        self.assertEqual(integration.name, "Test Shopify Store")
        self.assertEqual(integration.integration_type, "shopify")
        self.assertEqual(integration.tenant, self.tenant)
        self.assertTrue(integration.is_enabled)


class IntegrationAPITest(APITestCase):
    """Test Integration API endpoints"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
        self.client.force_authenticate(user=self.user)
        
        self.integration = Integration.objects.create(
            tenant=self.tenant,
            name="Test Integration",
            integration_type="shopify",
            status="active"
        )
    
    def test_list_integrations(self):
        """Test listing integrations"""
        url = reverse('integration-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Test Integration")
    
    def test_create_integration(self):
        """Test creating an integration"""
        url = reverse('integration-list')
        data = {
            'name': 'New Integration',
            'integration_type': 'woocommerce',
            'status': 'active',
            'base_url': 'https://example.com'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Integration.objects.count(), 2)
        self.assertEqual(Integration.objects.last().name, "New Integration")
    
    def test_get_integration(self):
        """Test retrieving an integration"""
        url = reverse('integration-detail', kwargs={'pk': self.integration.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Integration")
    
    def test_update_integration(self):
        """Test updating an integration"""
        url = reverse('integration-detail', kwargs={'pk': self.integration.pk})
        data = {'name': 'Updated Integration'}
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.integration.refresh_from_db()
        self.assertEqual(self.integration.name, "Updated Integration")
    
    def test_delete_integration(self):
        """Test deleting an integration"""
        url = reverse('integration-detail', kwargs={'pk': self.integration.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Integration.objects.count(), 0)
    
    @patch('integrations.views.requests.get')
    def test_test_connection_shopify(self, mock_get):
        """Test Shopify connection test"""
        # Mock successful Shopify API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'shop': {'name': 'Test Shop'}
        }
        mock_get.return_value = mock_response
        
        # Update integration with Shopify config
        self.integration.config = {'shop_domain': 'test-shop'}
        self.integration.api_key = 'test_key'
        self.integration.save()
        
        url = reverse('integration-test-connection', kwargs={'pk': self.integration.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['shop_name'], 'Test Shop')
    
    def test_sync_integration(self):
        """Test manual sync trigger"""
        url = reverse('integration-sync', kwargs={'pk': self.integration.pk})
        data = {'sync_type': 'products'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sync_id', response.data)
        
        # Check that sync record was created
        sync = IntegrationSync.objects.get(integration=self.integration)
        self.assertEqual(sync.sync_type, 'products')
        self.assertEqual(sync.direction, 'import')


class WebhookTest(TestCase):
    """Test webhook handling"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant"
        )
        self.integration = Integration.objects.create(
            tenant=self.tenant,
            name="Test Integration",
            integration_type="shopify",
            status="active"
        )
        self.client = Client()
    
    def test_shopify_webhook(self):
        """Test Shopify webhook processing"""
        url = reverse('shopify_webhook')
        
        # Mock webhook data
        webhook_data = {
            'id': 12345,
            'name': 'Test Order',
            'total_price': '100.00'
        }
        
        headers = {
            'X-Shopify-Shop-Domain': 'test-shop.myshopify.com',
            'X-Shopify-Topic': 'orders/create',
            'X-Shopify-Hmac-Sha256': 'test_signature'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            **headers
        )
        
        # Should return 404 since we don't have a ShopifyStore configured
        self.assertEqual(response.status_code, 404)
    
    def test_woocommerce_webhook(self):
        """Test WooCommerce webhook processing"""
        url = reverse('woocommerce_webhook')
        
        webhook_data = {
            'id': 12345,
            'status': 'completed',
            'total': '100.00'
        }
        
        headers = {
            'X-WC-Webhook-Topic': 'order.created',
            'X-WC-Webhook-ID': '123'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_data),
            content_type='application/json',
            **headers
        )
        
        # Should return 404 since we don't have a WooCommerceStore configured
        self.assertEqual(response.status_code, 404)


class ImportTest(APITestCase):
    """Test CSV import functionality"""
    
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant"
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            tenant=self.tenant
        )
        self.client.force_authenticate(user=self.user)
    
    def test_import_products_csv(self):
        """Test importing products from CSV"""
        url = reverse('import_data')
        
        # Create test CSV content
        csv_content = "sku,name,description,cost_price,selling_price,reorder_point,reorder_quantity\n"
        csv_content += "TEST-001,Test Product,Test Description,10.00,15.00,5,20\n"
        csv_content += "TEST-002,Another Product,Another Description,20.00,30.00,10,50\n"
        
        # Create a mock file
        from django.core.files.uploadedfile import SimpleUploadedFile
        csv_file = SimpleUploadedFile(
            "products.csv",
            csv_content.encode(),
            content_type="text/csv"
        )
        
        data = {
            'file': csv_file,
            'type': 'products'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('records_processed', response.data)
        self.assertIn('records_created', response.data)
    
    def test_import_without_file(self):
        """Test import without file"""
        url = reverse('import_data')
        data = {'type': 'products'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No file provided', response.data['error'])