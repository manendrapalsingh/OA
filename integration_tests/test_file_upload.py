from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File

class FileUploadIntegrationTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-list')

    def test_file_upload_success(self):
        file_content = b"Hello, world!"
        file = SimpleUploadedFile("hello.txt", file_content, content_type="text/plain")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(File.objects.first().original_filename, "hello.txt")

    def test_file_upload_no_file(self):
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(File.objects.count(), 0)

    def test_file_upload_invalid_file_type(self):
        file_content = b"Invalid content"
        file = SimpleUploadedFile("invalid.exe", file_content, content_type="application/octet-stream")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Assuming no file type validation
        self.assertEqual(File.objects.count(), 1) 