from django.db import models
from accounts.models import Recruiter
# Create your models here.
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('0-1', '0-1 Years'),
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10-20', '10-20 Years'),
        ('20-30', '20-30 Years'),
        ('30-40', '30-40 Years'),
        ('40-50', '40-50 Years'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    recruiter = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title