from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from threading import Thread
from django.core.mail import EmailMessage
from .models import Doctor, User

def send_email(subject, message, sender, recipient_list):
    email = EmailMessage(subject, message, sender, recipient_list)
    email.send()

@receiver(post_save, sender=Doctor)
def send_notification_on_new_event(sender, instance, created, **kwargs):
    if created:
        doctor = instance
        subject = f'New doctor Added'
        message = f'A new Doctor is added. Please verify.\n Username : {doctor.doctor.username}'
        admins = User.objects.filter(is_admin=True)

        for admin in admins:
            email_thread = Thread(
                target=send_email, args=(subject, message, settings.EMAIL_HOST_USER, [admin.email])
            )
            email_thread.start()
