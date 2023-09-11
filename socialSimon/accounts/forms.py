from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    user_email = forms.EmailField(required=True, label="School Email")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("user_email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
