from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .validators import validate_password
from .models import User, HOUR_CHOICES, STATUS_CHOICE


class UserLoginForm(forms.Form):

    email = forms.EmailField(label='Email', max_length=64)
    password = forms.CharField(label='Hasło', max_length=64, widget=forms.PasswordInput())

    def clean(self):

        super().clean()
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.filter(email=email).first()

        if user:
            
            if not user.is_active:
                self.add_error('email', 'Twoje konto nie zostało jeszcze aktywowane, sprawdź pocztę email')
            
            elif not authenticate(email=email, password=password):
                self.add_error('password', 'Błędne hasło')
        
        else:

            self.add_error('email', 'Email nie zarejestrowany w bazie danych')

    def authenticate_user(self):

        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = authenticate(email=email, password=password)

        return user    


class UserPasswordForm(forms.Form):

    password_check = forms.CharField(label='Poprzenie hasło', max_length=64)
    password_new = forms.CharField(label='Nowe hasło', max_length=64, validators=[validate_password])
    password_repeat = forms.CharField(label='Powtórz hasło', max_length=64)
    email = forms.CharField(widget=forms.HiddenInput())

    def clean(self):

        password_check = self.cleaned_data['password_check']
        password_new = self.cleaned_data['password_new']
        password_repeat = self.cleaned_data['password_repeat']
        email = self.cleaned_data['email']

        if validate_password(password_new):
            self.add_error('password_new', validate_password(password_new))

        if password_new != password_repeat:
            self.add_error('password_repeat', 'Nowe hasła róźnią się od siebie')

        if not authenticate(email=email, password=password_check):
            self.add_error('password_check', 'Błędne hasło')
