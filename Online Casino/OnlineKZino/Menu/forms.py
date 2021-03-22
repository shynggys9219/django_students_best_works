from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser



        fields = ('username',
                  'first_name',


                  'last_name',
                  'email',
                  'profile_pic'
                  )



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)



class SettingsForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    profile_pic = forms.ImageField(required=False)



