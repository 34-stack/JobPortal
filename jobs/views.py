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


class JobViewSet(viewsets.ModelViewSet):
    """
    Handles all job operations:
      list           → GET    /api/jobs/
      create         → POST   /api/jobs/
      retrieve       → GET    /api/jobs/<pk>/
      update         → PUT    /api/jobs/<pk>/
      partial_update → PATCH  /api/jobs/<pk>/
      destroy        → DELETE /api/jobs/<pk>/
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location', 'job_type', 'recruiter']  # ?location=mumbai
    search_fields = ['title', 'description']                  # ?search=keyword
    ordering_fields = ['posted_at', 'title']                  # ?ordering=posted_at

    def get_permissions(self):
        """
        list/retrieve → anyone can view (no auth needed)
        create        → must be a recruiter
        update/delete → must be a recruiter AND the owner of that job
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsRecruiterOrReadOnly(), IsOwnerOrReadOnly()]
        return [IsRecruiterOrReadOnly()]

    def perform_create(self, serializer):
        # Prevents invalid users from creating jobs.
        # Checks if the user is a recruiter and assigns the job to them.
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
        """GET /api/jobs/<pk>/applicants/ - Recruiter only"""
        job = self.get_object()
        if request.user.role != 'RECRUITER':
            return Response({"error": "Unauthorized"}, status=403)
        apps = Application.objects.filter(job=job)
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data)
 
