from django.db import models

# Create your models here.
class Application(models.Model):
    job=models.ForeignKey('jobs.job',on_delete=models.CASCADE)
    candidate= models.ForeignKey('accounts.Candidate',on_delete=models.CASCADE)
    cover_letter=models.TextField(blank=True)
    resume=models.FileField(upload_to='resumes/', blank=True, null=True)
    applied_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')],default='pending')
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = [("job", "candidate")]
    def __str__(self):
        return f"Application by {self.candidate.user.email} for {self.job.title}"