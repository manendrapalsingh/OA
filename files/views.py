from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import datetime
from .models import File
from .serializers import FileSerializer

# Create your views here.

class FileFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # Get filter parameters
        file_type = request.query_params.get('file_type')
        min_size = request.query_params.get('min_size')
        max_size = request.query_params.get('max_size')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Apply filters
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        if min_size:
            queryset = queryset.filter(size__gte=min_size)
        
        if max_size:
            queryset = queryset.filter(size__lte=max_size)
        
        if start_date:
            queryset = queryset.filter(uploaded_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(uploaded_at__lte=end_date)
        
        return queryset

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [filters.SearchFilter, FileFilter]
    search_fields = ['original_filename', 'file_type']
    
    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_obj)
        
        # Check for existing file with same hash
        existing_file = File.objects.filter(file_hash=file_hash).first()
        
        if existing_file:
            # Increment reference count for existing file
            existing_file.reference_count += 1
            existing_file.save()
            
            # Create a new file entry as a reference
            data = {
                'file': existing_file.file,  # Use existing file
                'original_filename': file_obj.name,
                'file_type': file_obj.content_type,
                'size': file_obj.size,
                'file_hash': file_hash,
                'is_duplicate': True
            }
        else:
            # Create new file entry
            data = {
                'file': file_obj,
                'original_filename': file_obj.name,
                'file_type': file_obj.content_type,
                'size': file_obj.size,
                'file_hash': file_hash,
                'is_duplicate': False
            }
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def storage_stats(self, request):
        """Get storage statistics including deduplication savings"""
        total_files = File.objects.count()
        unique_files = File.objects.filter(is_duplicate=False).count()
        storage_savings = File.get_storage_savings()
        
        return Response({
            'total_files': total_files,
            'unique_files': unique_files,
            'storage_savings_bytes': storage_savings,
            'storage_savings_mb': round(storage_savings / (1024 * 1024), 2)
        })
