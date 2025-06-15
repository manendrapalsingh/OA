from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File

class StorageStatsIntegrationTests(APITestCase):
    def setUp(self):
        self.stats_url = reverse('file-storage-stats')

    def test_storage_stats_success(self):
        # Upload a file
        file_content = b"Hello, world!"
        file = SimpleUploadedFile("hello.txt", file_content, content_type="text/plain")
        self.client.post(reverse('file-list'), {'file': file}, format='multipart')
        # Check storage stats
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_files', response.data)
        self.assertIn('unique_files', response.data)
        self.assertIn('storage_savings_bytes', response.data)
        self.assertIn('storage_savings_mb', response.data)

    def test_storage_stats_no_files(self):
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_files'], 0)
        self.assertEqual(response.data['unique_files'], 0)
        self.assertEqual(response.data['storage_savings_bytes'], 0)
        self.assertEqual(response.data['storage_savings_mb'], 0) 