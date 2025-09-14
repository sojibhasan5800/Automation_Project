from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model 
from django import forms

User = get_user_model()
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # username automatically from email
        user.username = self.cleaned_data['email'].split('@')[0]
        if commit:
            user.save()
        return user