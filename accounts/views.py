from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Candidate, Recruiter
from .serializers import (
    CandidateSerializer,
    LoginSerializer,
    RecruiterSerializer,
    RegisterSerializer,
    UserSerializer,
)
from applications.models import Application
from jobs.models import Job



class AuthViewSet(viewsets.ViewSet):
    """Handles user registration and login. No authentication required."""
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = UserSerializer(user).data

        # Attach role-specific profile in the response
        if user.role == "RECRUITER" and hasattr(user, "recruiter"):
            response_data["recruiter_profile"] = RecruiterSerializer(
                user.recruiter, context={"request": request}
            ).data
        elif user.role == "CANDIDATE" and hasattr(user, "candidate"):
            response_data["candidate_profile"] = CandidateSerializer(
                user.candidate, context={"request": request}
            ).data

        return Response(response_data, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['get'])
    def dashboard(self,request):
        user = request.user
        if user.role == "CANDIDATE":
            data = {
                "total_applications": Application.objects.filter(candidate__user=user).count(),
                "status_breakdown": {
                    "pending": Application.objects.filter(candidate__user=user, status='pending').count(),
                    "accepted": Application.objects.filter(candidate__user=user, status='accepted').count(),
                    "rejected": Application.objects.filter(candidate__user=user, status='rejected').count(),
                }
            }
        elif user.role == "RECRUITER":
            data = {
            "total_jobs_posted": Job.objects.filter(recruiter__user=user).count(),
            "active_jobs": Job.objects.filter(recruiter__user=user, is_active=True).count(),
            "total_applicants_received": Application.objects.filter(job__recruiter__user=user).count(),
            }
                

            return Response(data)
    @action(detail=False, methods=['post'],url_path='change-password')
    def change_password(self,request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(old_password):
            return Response({"detail":"Old password is incorrect"},status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"detail":"Password changed successfully"},status=status.HTTP_200_OK)
            

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class RecruiterViewSet(viewsets.ViewSet):
    """Handles recruiter profile creation and self-management."""
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """POST /api/accounts/recruiter/ — Create recruiter profile for logged-in user."""
        # BUG FIX: prevent duplicate profile crash (OneToOne constraint)
        # Registration already auto-creates the profile, so this endpoint
        # is only needed if someone registered as ADMIN and wants to add a recruiter profile.
        if hasattr(request.user, 'recruiter'):
            return Response(
                {"detail": "Recruiter profile already exists. Use PATCH /api/accounts/recruiter/me/ to update it."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecruiterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def me(self, request):
        """GET/PUT/PATCH/DELETE /api/accounts/recruiter/me/ — Manage own recruiter profile."""
        recruiter = get_object_or_404(Recruiter, user=request.user)

        if request.method == 'GET':
            return Response(RecruiterSerializer(recruiter, context={"request": request}).data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = RecruiterSerializer(
                recruiter, data=request.data, partial=partial, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            recruiter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateViewSet(viewsets.ViewSet):
    """Handles candidate profile creation and self-management."""
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """POST /api/accounts/candidate/ — Create candidate profile for logged-in user."""
        # BUG FIX: prevent duplicate profile crash (OneToOne constraint)
        # Registration already auto-creates the profile, so block double-creation here.
        if hasattr(request.user, 'candidate'):
            return Response(
                {"detail": "Candidate profile already exists. Use PATCH /api/accounts/candidate/me/ to update it."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CandidateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch', 'delete'])
    def me(self, request):
        """GET/PUT/PATCH/DELETE /api/accounts/candidate/me/ — Manage own candidate profile."""
        candidate = get_object_or_404(Candidate, user=request.user)

        if request.method == 'GET':
            return Response(CandidateSerializer(candidate, context={"request": request}).data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = CandidateSerializer(
                candidate, data=request.data, partial=partial, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            candidate.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
