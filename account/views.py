from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from .forms import RegistrationForm
from .models import OtpToken
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from dataentry.utlis import generate_tracking_email_user
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("account:verify-email",  username=user.username)
        else:
            context = {'form': form}
            return render(request, 'accounts/register.html', context)
    else:
        form = RegistrationForm()
        context = {
            'form': form,
        }
    return render(request, 'accounts/register.html', context)

def verify_email(request,username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
   
    
    if request.method == 'POST':
        

        # valid token
        if user_otp.otp_code == request.POST['otp_code']:
           
            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active=True
                user.save()
                # Testing generate email for developer in Bulk Email Tracking
                generate_tracking_email_user(user.email)

                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("account:login")
            
            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("account:verify-email", username=user.username)
        
        
        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("account:verify-email", username=user.username)
        
    context = {
        'username':username
    }
    return render(request, "accounts/verify_token.html", context)


def auto_active_verify_email(request,username,uidb64):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    # valid token
    uid = urlsafe_base64_decode(uidb64).decode()
    if user_otp.otp_code == uid:
        
        # checking for expired token
        if user_otp.otp_expires_at > timezone.now():
            user.is_active=True
            user.save()
            messages.success(request, "Account activated successfully!! You can Login.")
            return redirect("account:login")
        
        # expired token
        else:
            messages.warning(request, "The OTP has expired, get a new OTP!")
            return redirect("account:verify-email", username=user.username)
    
    
    # invalid otp code
    else:
        messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
        return redirect("account:verify-email", username=user.username)
    
   

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=2))
            
            otp_codes = otp.otp_code
            uidb64= urlsafe_base64_encode(force_bytes(otp_codes))
            # context data
            context = {
                "username": user.username,
                "otp": otp_codes,
                "verify_url": f"https://automation-project-chst.onrender.com/account/verify-email/{user.username}/{uidb64}",
            }
            
            
            
            # HTML Template render
            subject = "Verify Your Email Address"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]

            text_content = render_to_string("accounts/otp_email.txt", context)  # fallback text
            html_content = render_to_string("accounts/otp_email.html", context)  # beautiful design

            # Email send
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
                
            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("account:verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("account:resend-otp")
        
           
    context = {}
    return render(request, "accounts/resend_otp.html", context)


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
            return redirect('account:login')
    else:
        form = AuthenticationForm()
        context = {'form': form,}
    return render(request, 'accounts/login.html', context)

def logout(request):
    auth.logout(request)
    return redirect('home')

