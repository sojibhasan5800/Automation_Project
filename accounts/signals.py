from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

 
@receiver(post_save, sender=settings.AUTH_USER_MODEL) 
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            return
        
        else:
            
            OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=2))
            instance.is_active=False 
            instance.save(update_fields=["is_active"])
        
        
        # email credentials
        otp = OtpToken.objects.filter(user=instance).last()
        otp_codes = otp.otp_code
        uidb64= urlsafe_base64_encode(force_bytes(otp_codes))
        # context data
        context = {
            "username": instance.username,
            "otp": otp_codes,
            "verify_url": f"https://automation-project-chst.onrender.com/accounts/verify-email/{instance.username}/{uidb64}",
        }
       
        
        
        # HTML Template render
        subject = "Verify Your Email Address"
        from_email = settings.EMAIL_HOST_USER
        print(from_email)
        to_email = [instance.email]
        print(to_email)
        
        text_content = render_to_string("accounts/otp_email.txt", context)  # fallback text
        html_content = render_to_string("accounts/otp_email.html", context)  # beautiful design

        # Email send
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("passing")
  