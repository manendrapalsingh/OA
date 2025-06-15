from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import File
import io

class FileUploadTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-list')

    def test_file_upload(self):
        file_content = b"Hello, world!"
        file = SimpleUploadedFile("hello.txt", file_content, content_type="text/plain")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(File.objects.first().original_filename, "hello.txt")

    def test_file_deduplication(self):
        file_content = b"Duplicate content"
        file1 = SimpleUploadedFile("dup1.txt", file_content, content_type="text/plain")
        file2 = SimpleUploadedFile("dup2.txt", file_content, content_type="text/plain")
        # Upload first file
        response1 = self.client.post(self.upload_url, {'file': file1}, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        # Upload duplicate file
        response2 = self.client.post(self.upload_url, {'file': file2}, format='multipart')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        # There should be two File records, but only one unique file_hash
        self.assertEqual(File.objects.count(), 2)
        hashes = set(File.objects.values_list('file_hash', flat=True))
        self.assertEqual(len(hashes), 1)
        # One should be marked as duplicate
        self.assertTrue(File.objects.filter(is_duplicate=True).exists())

    def test_file_filtering(self):
        # Upload files with different types and sizes
        file1 = SimpleUploadedFile("a.txt", b"A"*10, content_type="text/plain")
        file2 = SimpleUploadedFile("b.pdf", b"B"*100, content_type="application/pdf")
        self.client.post(self.upload_url, {'file': file1}, format='multipart')
        self.client.post(self.upload_url, {'file': file2}, format='multipart')
        # Filter by file_type
        response = self.client.get(self.upload_url + '?file_type=application/pdf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['file_type'], 'application/pdf')
        # Filter by size range
        response = self.client.get(self.upload_url + '?min_size=50')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_filename'], 'b.pdf')
        # Filter by multiple criteria
        response = self.client.get(self.upload_url + '?file_type=text/plain&max_size=20')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['original_filename'], 'a.txt') 