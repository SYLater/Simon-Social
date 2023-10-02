from django import forms
from .models import User

class UserLoginForm(forms.Form):
    user_email = forms.CharField(label="School Email/Username", required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("user_email", "password")
