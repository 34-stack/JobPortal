from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """
    'candidate' is read-only because it is set automatically from
    the logged-in user in the view (perform_create), not from request body.

    'id' and 'applied_at' are read-only because they are auto-generated
    by the database and should never be sent by the client.

    'status' is included here so recruiters can see the current status
    when listing applications, but changing it is handled by a separate
    endpoint using ApplicationStatusUpdateSerializer below.
    """

    class Meta:
        model = Application
        fields = [
            'id',           # auto-generated primary key
            'job',          # FK to Job — candidate picks the job they want to apply to
            'candidate',    # FK to Candidate — auto-assigned from logged-in user
            'cover_letter', # candidate writes why they want the job
            'resume',       # candidate uploads a resume for this specific application
            'applied_at',   # auto-set timestamp when application is created
            'status',       # pending / accepted / rejected
        ]
        read_only_fields = [
            'id',           # never sent by client
            'applied_at',   # auto-set on creation
            'candidate',    # assigned from request.user in the view, not from body
        ]


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Used ONLY for:
      - Recruiter updating application status (PATCH /api/applications/<pk>/update-status/)

    We intentionally expose ONLY the 'status' field here.
    This prevents a recruiter (or any user) from accidentally or
    maliciously modifying 'job', 'cover_letter', 'resume', etc.
    through the status-update endpoint.
    """

    class Meta:
        model = Application
        fields = ['id', 'status']   # only 'status' is writable; 'id' shown for reference
        read_only_fields = ['id']