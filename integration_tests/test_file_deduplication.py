from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File

class FileDeduplicationIntegrationTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('file-list')

    def test_file_deduplication_success(self):
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

    def test_file_deduplication_different_content(self):
        file1 = SimpleUploadedFile("file1.txt", b"Content 1", content_type="text/plain")
        file2 = SimpleUploadedFile("file2.txt", b"Content 2", content_type="text/plain")
        # Upload first file
        response1 = self.client.post(self.upload_url, {'file': file1}, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        # Upload second file with different content
        response2 = self.client.post(self.upload_url, {'file': file2}, format='multipart')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        # There should be two File records with different hashes
        self.assertEqual(File.objects.count(), 2)
        hashes = set(File.objects.values_list('file_hash', flat=True))
        self.assertEqual(len(hashes), 2)
        # None should be marked as duplicate
        self.assertFalse(File.objects.filter(is_duplicate=True).exists()) 