from djnago.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application

@receiver(post_save, sender = Application)


def notify_candidate_on_status_change(sender, instance, created, **kwargs):
     
     if not created:
        subject = f"Update on your applications for {instance.job.title}"
        
        if instance.status == 'accepted':
            message = f"Congratulations! Your application for the role of {instance.job.title} has been accepted."
        elif instance.status == 'rejected':
            message = f"We regret to inform you that your application for the role of {instance.job.title} has been rejected.Don't lose hope, keep applying!"
        else:
            return
        send_mail(subject, message, 'support@ummahjobs.com',[instance.candidate.user.email],fail_silently=False)