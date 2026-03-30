from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager

from django.db import models
from base.models import TimeStampedModel
from base.validators import validate_resume_extension, validate_file_size

CANDIDATE = "CANDIDATE"
RECRUITER = "RECRUITER"
ADMIN = "ADMIN"

class roles(TimeStampedModel):
    name = models.CharField(max_length = 20, unique = True)
    code = models.CharField(max_length = 20, unique = True)
    is_active = models.BooleanField(default = True)
    
class WorkDetails(TimeStampedModel):
    company_name = models.CharField(max_length = 255)
    designation = models.CharField(max_length = 255)
    start_date = models.DateField()
    end_date = models.DateField(null = True, blank = True)
    currently_working  = models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, TimeStampedModel):
    username = None
    role = models.ForeignKey(roles, on_delete=models.CASCADE, related_name='users_primary_role', null=True, blank=True)
    work_details = models.ForeignKey(WorkDetails, on_delete=models.CASCADE, related_name='users_current_work', null=True, blank=True)
    name = models.CharField(max_length=128, blank=True, null=True, default='')
    mobile = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    image = models.CharField(max_length=1024, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,blank=True, null=True)
    experience_yrs = models.IntegerField(blank=True, null=True)
    experience_month = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    cv = models.FileField(upload_to='resumes/', blank=True, null=True, validators = [validate_resume_extension, validate_file_size])
    current_ctc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_ctc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    work_experience = models.ManyToManyField(WorkDetails, blank=True, related_name='users_work_experience')


    date_range = models.CharField(max_length=255, blank=True, null=True)
    # Employer-specific fields
    organisation_name = models.CharField(max_length=255, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()
    roles_list = models.ManyToManyField(roles, related_name='users_roles_list')


    # Email address =  the username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile']
    class Meta:
        verbose_name_plural = 'Users'
    def __str__(self):
        return self.email
      

class UserOTP(TimeStampedModel):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT, related_name="user_otp")
    otp = models.CharField(max_length=15, blank=True, null=True)
    counter = models.IntegerField(blank=True, default=25)
    resend_counter = models.IntegerField(blank=True, default=25)
    is_active = models.BooleanField(default=True)

class UserEmailVerification(TimeStampedModel):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT, related_name="user_email_verification")
    code = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)

# Proxy models for admin separation
class Candidate(User):
    """Proxy model for Candidate admin interface"""
    class Meta:
        proxy = True
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'


class Employer(User):
    """Proxy model for Employer admin interface"""
    class Meta:
        proxy = True
        verbose_name = 'Employer'
        verbose_name_plural = 'Employers'

class Recruiter(User):
    """Proxy model for Recruiter admin interface"""
    class Meta:
        proxy = True
        verbose_name = 'Recruiter'
        verbose_name_plural = 'Recruiters'



class UserSession(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='session_user')
    jti = models.CharField(max_length=255, unique=True)
    refresh_token = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"
    
    
    