from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File

class FileFilteringIntegrationTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-list')
        # Upload files with different types and sizes
        file1 = SimpleUploadedFile("a.txt", b"A"*10, content_type="text/plain")
        file2 = SimpleUploadedFile("b.pdf", b"B"*100, content_type="application/pdf")
        self.client.post(self.upload_url, {'file': file1}, format='multipart')
        self.client.post(self.upload_url, {'file': file2}, format='multipart')

    def test_filter_by_file_type(self):
        response = self.client.get(self.upload_url + '?file_type=application/pdf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['file_type'], 'application/pdf')

    def test_filter_by_size_range(self):
        response = self.client.get(self.upload_url + '?min_size=50')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_filename'], 'b.pdf')

    def test_filter_by_multiple_criteria(self):
        response = self.client.get(self.upload_url + '?file_type=text/plain&max_size=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_filename'], 'a.txt')

    def test_filter_no_results(self):
        response = self.client.get(self.upload_url + '?file_type=image/jpeg')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 