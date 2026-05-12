from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings 

from .models import Application
from .serializers import ApplicationSerializer, ApplicationStatusUpdateSerializer
from accounts.models import CANDIDATE, RECRUITER


class ApplicationViewSet(
    mixins.CreateModelMixin,   # POST /api/applications/
    mixins.ListModelMixin,     # GET  /api/applications/  (role-filtered)
    viewsets.GenericViewSet    # base — no retrieve/update/destroy exposed
):
    """
    Only exposes:
      create        → POST  /api/applications/
      list          → GET   /api/applications/          (scoped to logged-in user's role)
      update_status → PATCH /api/applications/<pk>/update-status/  (recruiter only)

    ModelViewSet is intentionally NOT used here to avoid exposing
    unprotected retrieve/update/destroy endpoints.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update_status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer

    def get_queryset(self):
        """
        Candidates see only their own applications.
        Recruiters see all applications for their jobs.
        """
        user = self.request.user
        if user.role == CANDIDATE:
            return Application.objects.filter(candidate=user.candidate)
        elif user.role == RECRUITER:
            return Application.objects.filter(job__recruiter=user.recruiter)
        return Application.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != CANDIDATE:
            raise ValidationError("Only candidates can apply for jobs.")

        # Save the application and keep the instance
        application = serializer.save(candidate=self.request.user.candidate)

        # Email data
        job = application.job
        recruiter_email = job.recruiter.email
        candidate_email = self.request.user.email
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            # Email to Recruiter
            send_mail(
                subject=f"New Application: {job.title}",
                message=(
                    f"Hello,\n\n"
                    f"A new candidate ({candidate_email}) has applied for your job: {job.title}.\n"
                    f"Please log in to review the application."
                ),
                from_email=from_email,
                recipient_list=[recruiter_email],
            )

            # Confirmation email to Candidate
            send_mail(
                subject=f"Application Submitted: {job.title}",
                message=(
                    f"Hello,\n\n"
                    f"Your application for \"{job.title}\" has been received.\n"
                    f"We will notify you when the recruiter updates the status."
                ),
                from_email=from_email,
                recipient_list=[candidate_email],
            )
        except Exception as e:
            print(f"Error sending email: {e}")




        


    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk):
        """PATCH /api/applications/<pk>/update-status/ — Recruiter updates status only."""
        application = self.get_object()
        if request.user.role != RECRUITER:
            raise ValidationError("Only recruiters can update the application status.")
        serializer = ApplicationStatusUpdateSerializer(
            application, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
