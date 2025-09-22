from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from .forms import RegistrationForm
from .models import OtpToken
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from dataentry.utlis import generate_tracking_email_user
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

#  Correct import (django-ratelimit)
from django_ratelimit.decorators import ratelimit
from .share_ip import user_or_ip


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created! Please verify your email with the OTP sent to you.")
            return redirect("accounts:verify-email", username=user.username)
        else:
            context = {'form': form}
            return render(request, 'accounts/register.html', context)
    else:
        form = RegistrationForm()
        context = {'form': form}
    return render(request, 'accounts/register.html', context)


@ratelimit(key=user_or_ip, rate='5/m', method='POST', block=True)
def verify_email(request, username):
    """Verify OTP with rate limiting"""
    try:
        user = get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
        messages.warning(request, "Invalid user.")
        return redirect("accounts:login")
    
    user_otp = OtpToken.objects.filter(user=user).last()
    if not user_otp:
        messages.warning(request, "No OTP found for this user, please request a new one.")
        return redirect("accounts:resend-otp", username=user.username)
    
    now = timezone.now()
    time_left = max((user_otp.otp_expires_at - now).total_seconds(), 0)

    if request.method == 'POST':
        if user_otp.otp_code == request.POST['otp_code']:
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                generate_tracking_email_user(user.email)
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("accounts:login")
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("accounts:verify-email", username=user.username)
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("accounts:verify-email", username=user.username)

    return render(request, "accounts/verify_token.html", {"username": username})


def auto_active_verify_email(request, username, uidb64):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    uid = urlsafe_base64_decode(uidb64).decode()

    if user_otp.otp_code == uid:
        if user_otp.otp_expires_at > timezone.now():
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully!! You can Login.")
            return redirect("accounts:login")
        else:
            messages.warning(request, "The OTP has expired, get a new OTP!")
            return redirect("accounts:verify-email", username=user.username)
    else:
        messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
        return redirect("accounts:verify-email", username=user.username)


@ratelimit(key='post:otp_email', rate='2/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def resend_otp(request, username):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            cache_key = f"otp_{user.email}"
            otp_codes = cache.get(cache_key)

            if not otp_codes:
                otp = OtpToken.objects.create(
                    user=user,
                    otp_expires_at=timezone.now() + timezone.timedelta(minutes=2)
                )
                otp_codes = otp.otp_code
                cache.set(cache_key, otp_codes, timeout=120)

            uidb64 = urlsafe_base64_encode(force_bytes(otp_codes))
            site_url = settings.BASE_URL

            context = {
                "username": user.username,
                "otp": otp_codes,
                "verify_url": f"{site_url}/accounts/verify-email/{user.username}/{uidb64}",
            }

            subject = "Verify Your Email Address"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            text_content = render_to_string("accounts/otp_email.txt", context)
            html_content = render_to_string("accounts/otp_email.html", context)

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("accounts:verify-email", username=user.username)

        else:
            messages.warning(request, "This email doesn't exist in the database")
            return redirect("accounts:resend-otp")

    return render(request, "accounts/resend_otp.html", {"username": username})


@ratelimit(key=user_or_ip, rate='5/m', method='POST', block=True)
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('accounts:login')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    return redirect('home')
