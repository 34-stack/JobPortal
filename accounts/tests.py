from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import ADMIN, CANDIDATE, RECRUITER, Candidate, Recruiter


class UserModelTests(TestCase):
    def test_create_user_with_unique_email(self):
        user = get_user_model().objects.create_user(
            email="candidate1@example.com",
            password="Pass@1234",
            role=CANDIDATE,
        )
        self.assertEqual(user.email, "candidate1@example.com")

    def test_duplicate_email_fails(self):
        get_user_model().objects.create_user(
            email="dup@example.com",
            password="Pass@1234",
            role=CANDIDATE,
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email="dup@example.com",
                password="Pass@1234",
                role=RECRUITER,
            )

    def test_login_with_email_and_password(self):
        user = get_user_model().objects.create_user(
            email="login@example.com",
            password="Pass@1234",
            role=CANDIDATE,
        )
        authenticated = authenticate(username="login@example.com", password="Pass@1234")
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.pk, user.pk)

    def test_role_required_and_restricted(self):
        with self.assertRaises(ValidationError):
            user = get_user_model()(email="badrole@example.com", role="INVALID")
            user.full_clean()

        with self.assertRaises(ValidationError):
            user = get_user_model()(email="norole@example.com")
            user.full_clean()

    def test_recruiter_blocked_for_candidate_role(self):
        user = get_user_model().objects.create_user(
            email="cand@example.com",
            password="Pass@1234",
            role=CANDIDATE,
        )

        with self.assertRaises(ValidationError):
            Recruiter.objects.create(
                user=user,
                company_name="Acme",
            )

    def test_candidate_blocked_for_recruiter_role(self):
        user = get_user_model().objects.create_user(
            email="rec@example.com",
            password="Pass@1234",
            role=RECRUITER,
        )

        with self.assertRaises(ValidationError):
            Candidate.objects.create(
                user=user,
                resume="resumes/resume.pdf",
            )

    def test_soft_deactivate_keeps_related_records(self):
        user = get_user_model().objects.create_user(
            email="soft@example.com",
            password="Pass@1234",
            role=CANDIDATE,
        )
        candidate = Candidate.objects.create(user=user, resume="resumes/resume.pdf")

        user.is_active = False
        user.save(update_fields=["is_active"])

        self.assertTrue(Candidate.objects.filter(pk=candidate.pk).exists())

    def test_admin_user_creation_and_login(self):
        admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="Pass@1234",
        )

        self.assertEqual(admin_user.role, ADMIN)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        logged_in = self.client.login(username="admin@example.com", password="Pass@1234")
        self.assertTrue(logged_in)
