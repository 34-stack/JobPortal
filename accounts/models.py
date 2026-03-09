from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.db import models

CANDIDATE = "CANDIDATE"
RECRUITER = "RECRUITER"
ADMIN = "ADMIN"

ROLE_CHOICES = [
    (CANDIDATE, "Candidate"),
    (RECRUITER, "Recruiter"),
    (ADMIN, "Admin"),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="recruiter")
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)



    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate")
    resume = models.FileField(upload_to="resumes/",blank=True,null=True)
    skills = models.TextField(blank=True,null=True)
    experience_years = models.PositiveIntegerField(default=0)

    

    def __str__(self):
        return self.user.email
