from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Application

@receiver(post_save, sender=Application)
def handle_application_emails(sender, instance, created, **kwargs):
    from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        if created:
            # Email to Recruiter
            job = instance.job
            if job and job.recruiter:
                recruiter_email = job.recruiter.email
                candidate_email = instance.candidate.email
                
                send_mail(
                    subject=f"New Application: {job.title}",
                    message=f"A new candidate ({candidate_email}) has applied for your job: {job.title}.",
                    from_email=from_email,
                    recipient_list=[recruiter_email],
                )

            # Confirmation email to Candidate
            if instance.candidate:
                send_mail(
                    subject=f"Application Submitted: {job.title}",
                    message=f"Your application for \"{job.title}\" has been received.",
                    from_email=from_email,
                    recipient_list=[instance.candidate.email],
                )
        else:
            # Email to Candidate on Status Change
            if instance.status in ['accepted', 'rejected']:
                subject = f"Update on your application for {instance.job.title}"
                message = f"Your application status for {instance.job.title} is now {instance.status}."
                send_mail(subject, message, from_email, [instance.candidate.email])
    except Exception as e:
        print(f"Error in application signal: {e}")