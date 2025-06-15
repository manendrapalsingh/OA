from django.db import models
import uuid
import os
import hashlib
from django.db.models import Sum

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

def calculate_file_hash(file_obj):
    """Calculate SHA-256 hash of file content"""
    sha256_hash = hashlib.sha256()
    for chunk in file_obj.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, unique=True, null=True)  # SHA-256 hash
    reference_count = models.IntegerField(default=1)  # Track number of references to this file
    is_duplicate = models.BooleanField(default=False)  # Flag to identify duplicate files
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['file_type']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return self.original_filename

    @classmethod
    def get_storage_savings(cls):
        """Calculate total storage savings from deduplication"""
        total_size = cls.objects.aggregate(total=Sum('size'))['total'] or 0
        unique_size = cls.objects.filter(is_duplicate=False).aggregate(total=Sum('size'))['total'] or 0
        return total_size - unique_size
