from django import forms
import datetime
from django.contrib.auth import authenticate
from django.db.models import Q
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from .validators import validate_password
from .models import User, Reservation, HOUR_CHOICES, STATUS_CHOICE, Room


class DateInput(forms.DateInput):
    
    input_type = 'date'


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


class UserPasswordUpdateForm(forms.Form):

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


class UserPasswordSetForm(forms.Form):

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


class UserPasswordResetForm(forms.Form):

    email = forms.EmailField(label='Email', max_length=64)

    def clean(self):

        cleaned_data = super().clean()
        
        email = cleaned_data['email']

        if User.objects.filter(email=email).count() != 1:
            self.add_error('email', 'Brak konta o podanym adresie email')


class ReservationAddForm(forms.ModelForm):
        
    class Meta:
        model = Reservation
        fields = ['room', 'patient', 'start_date', 'end_date', 'message']
        widgets = {
            'room': forms.HiddenInput(),
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

    def clean(self):
        
        cleaned_data = super().clean()

        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']
        patient = cleaned_data['patient']

        prev_reservation = patient.reservation_set.filter(end_date__range=(start_date, end_date)).order_by('-end_date').first()
        next_reservation = patient.reservation_set.filter(start_date__range=(start_date, end_date)).order_by('start_date').first()
        during_reservation = patient.reservation_set.filter(start_date__lte=start_date, end_date__gte=end_date).first()
        
        if prev_reservation:
            self.add_error(
                'patient', 
                f'Pacjent ma już zarezerwowany pobyt w tym terminie, {prev_reservation.start_date} - {prev_reservation.end_date}'
                )
        elif next_reservation:
            self.add_error(
                'patient', 
                f'Pacjent ma już zarezerwowany pobyt w tym terminie, {next_reservation.start_date} - {next_reservation.end_date}'
                )
        elif during_reservation:
            self.add_error(
                'patient', 
                f'Pacjent ma już zarezerwowany pobyt w tym terminie, {during_reservation.start_date} - {during_reservation.end_date}'
                )
        

class ReservationUpdateForm(forms.ModelForm):
        
    class Meta:
        model = Reservation
        fields = ['start_date', 'end_date', 'message']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

    def clean(self):
        
        cleaned_data = super().clean()

        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']
        
        reservation = self.instance
        prev_reservation = Reservation.objects.filter(
            patient=reservation.patient,
            end_date__range=(start_date, reservation.start_date)
            ).order_by('-end_date').first()
        next_reservation = Reservation.objects.filter(
            patient=reservation.patient,
            start_date__range=(reservation.end_date, end_date)
            ).order_by('start_date').first()

        if prev_reservation:
            self.add_error(
                NON_FIELD_ERRORS, 
                f'Pacjent ma już zarezerwowany pobyt w tym terminie, {prev_reservation.start_date} - {prev_reservation.end_date}'
                )
        elif next_reservation:
            self.add_error(
                NON_FIELD_ERRORS, 
                f'Pacjent ma już zarezerwowany pobyt w tym terminie, {next_reservation.start_date} - {next_reservation.end_date}'
                )
