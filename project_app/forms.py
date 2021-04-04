from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .validators import validate_tel_number
from .models import User, HOUR_CHOICES, STATUS_CHOICE


class UserLoginForm(forms.Form):

    username = forms.CharField(label='Login', max_length=64)
    password = forms.CharField(label='Hasło', max_length=64, widget=forms.PasswordInput())

    def clean(self):

        super().clean()
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if User.objects.filter(username=username).first():

            if not authenticate(username=username, password=password):
                self.add_error('password', 'Błędne hasło')
        else:

            self.add_error('username', 'Błędny login')

    def authenticate_user(self):

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)

        return user


class UserCreateForm(forms.Form):

    first_name = forms.CharField(label='Imię', max_length=64)
    last_name = forms.CharField(label='Nazwisko', max_length=64)
    email = forms.EmailField()
    tel_number = forms.CharField(label='Telefon (+48)', validators=[validate_tel_number])
    status = forms.ChoiceField(choices=STATUS_CHOICE, widget=forms.RadioSelect)
    
    # def clean(self):
    #     super().clean()
    #     password = self.cleaned_data['password']
    #     repeat_password = self.cleaned_data['repeat_password']
    #     if password != repeat_password:
    #         raise ValidationError('Hasła różnią się od siebie!')


# class MyUserUpdateForm(forms.Form):

#     nick = forms.CharField(label='Nick', max_length=64)
#     tel_number = forms.CharField(label='Telefon (+48)', validators=[validate_tel_number])
#     email = forms.EmailField()


# class MyUserPasswordForm(forms.Form):

#     password = forms.CharField(label='Hasło', max_length=64)
#     repeat_password = forms.CharField(label='Powtórz hasło', max_length=64)

#     def clean(self):
#         super(MyUserPasswordForm, self).clean()
#         password = self.cleaned_data['password']
#         repeat_password = self.cleaned_data['repeat_password']
#         if password != repeat_password:
#             raise ValidationError('Hasła różnią się od siebie!')

