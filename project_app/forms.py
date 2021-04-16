from django import forms
import datetime
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .validators import validate_password
from .models import User, Reservation, HOUR_CHOICES, STATUS_CHOICE, Room


class UserLoginForm(forms.Form):

    email = forms.EmailField(label='Email', max_length=64)
    password = forms.CharField(label='Hasło', max_length=64, widget=forms.PasswordInput())

    def clean(self):

        cleaned_data = super().clean()
        
        email = cleaned_data['email']
        password = cleaned_data['password']
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

        cleaned_data = super().clean()
        
        password_check = cleaned_data['password_check']
        password_new = cleaned_data['password_new']
        password_repeat = cleaned_data['password_repeat']
        email = cleaned_data['email']

        if validate_password(password_new):
            self.add_error('password_new', validate_password(password_new))

        if password_new != password_repeat:
            self.add_error('password_repeat', 'Nowe hasła róźnią się od siebie')

        if not authenticate(email=email, password=password_check):
            self.add_error('password_check', 'Błędne hasło')


class PasswordSetForm(forms.Form):

    password_new = forms.CharField(label='Nowe hasło', max_length=64, validators=[validate_password])
    password_repeat = forms.CharField(label='Powtórz hasło', max_length=64)

    def clean(self):

        cleaned_data = super().clean()
        
        password_new = cleaned_data['password_new']
        password_repeat = cleaned_data['password_repeat']

        if validate_password(password_new):
            self.add_error('password_new', validate_password(password_new))

        if password_new != password_repeat:
            self.add_error('password_repeat', 'Nowe hasła róźnią się od siebie')


class PasswordResetForm(forms.Form):

    email = forms.EmailField(label='Email', max_length=64)

    def clean(self):

        cleaned_data = super().clean()
        
        email = cleaned_data['email']

        if User.objects.filter(email=email).count() != 1:
            self.add_error('email', 'Brak konta o podanym adresie email')


class DateInput(forms.DateInput):
    
    input_type = 'date'


class ReservationAddForm(forms.ModelForm):

    room = forms.ModelChoiceField(queryset=Room.objects.all(), widget=forms.HiddenInput())
    start_reservation = forms.DateField(widget=DateInput(), label='Data rozpoczęcia')
    end_reservation = forms.DateField(widget=DateInput(), label='Data zakończenia')
    patient = forms.ModelChoiceField(
        queryset=User.objects.filter(status=3, is_active=True),
        label='Pacjent'
    )
    message = forms.CharField(widget=forms.Textarea(), label='Wiadomość', required=False)

    class Meta:
        
        model = Reservation
        fields = ['room', 'start_reservation', 'end_reservation', 'patient', 'message']

    def __init__(self, *args, **kwargs):
        
        start_date = kwargs.pop('start_date')
        end_date = kwargs.pop('end_date')
        
        super().__init__(*args, **kwargs)
        
        self.fields['start_reservation'].widget.attrs['min'] = start_date
        self.fields['start_reservation'].widget.attrs['max'] = end_date
        self.fields['end_reservation'].widget.attrs['min'] = start_date
        self.fields['end_reservation'].widget.attrs['max'] = end_date
    
    def clean(self):

        cleaned_data = super().clean()

        start_reservation = cleaned_data['start_reservation']
        end_reservation = cleaned_data['end_reservation']
        patient = cleaned_data['patient']
        
        if start_reservation >= end_reservation:
            self.add_error('end_reservation', 'Termin zakończenia musi być poźniej od rozpoczęcia')

        reservation_end = Reservation.objects.filter(
            patient=patient, end_reservation__range=(start_reservation, end_reservation)
        )
        reservation_start = Reservation.objects.filter(
            patient=patient, start_reservation__range=(start_reservation, end_reservation)
        )
        reservation_during = Reservation.objects.filter(
            patient=patient, start_reservation__lte=start_reservation, end_reservation__gte=end_reservation
        )

        if reservation_end or reservation_start or reservation_during:
            self.add_error('patient', 'Pacjent ma już zarezerwowany pobyt w tym terminie')
