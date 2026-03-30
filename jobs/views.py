from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Job
from .serializers import JobSerializer
from accounts.models import Recruiter
from applications.models import Application
from applications.serializers import ApplicationSerializer
from .permissions import IsOwnerOrReadOnly, IsRecruiterOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobFilter


class JobViewSet(viewsets.ModelViewSet):
    
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description','recruiter__organisation_name']                 
    ordering_fields = ['posted_at', 'title','salary']                 

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsRecruiterOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsRecruiterOrReadOnly()]

    def perform_create(self, serializer):
        recruiter = get_object_or_404(Recruiter, user=self.request.user)
        serializer.save(recruiter=recruiter)


    @action(detail=True, methods=['patch'], url_path='toggle-active')
    def toggle_active(self, request, pk=None):
           job = self.get_object()
           job.is_active = not job.is_active
           job.save()
           return Response({"id": job.id, "is_active": job.is_active})

    @action(detail=True, methods=['get'])
    def applicants(self, request, pk=None):
        job = self.get_object()
        if request.user.role != 'RECRUITER':
            return Response({"error": "Unauthorized"}, status=403)
        apps = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data)
 
