import datetime

from django import forms
from django.contrib.auth import authenticate
from django.db.models import Q
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import EmailValidator

from .validators import validate_password, validate_phone
from .models import User, Reservation, Room, Timetable
from .utils import change_day_to_date


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

    password_check = forms.CharField(label='Poprzenie hasło', max_length=64, widget=forms.PasswordInput())
    password_new = forms.CharField(label='Nowe hasło', max_length=64, widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', max_length=64, widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        
        self.email = kwargs.pop('email')

        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()

        password_check = cleaned_data['password_check']
        password_new = cleaned_data['password_new']
        password_repeat = cleaned_data['password_repeat']

        if validate_password(password_new):
            self.add_error('password_new', validate_password(password_new))

        if password_new != password_repeat:
            self.add_error('password_repeat', 'Nowe hasła róźnią się od siebie')

        if not authenticate(email=self.email, password=password_check):
            self.add_error('password_check', 'Błędne hasło')


class UserPasswordSetForm(forms.Form):

    password_new = forms.CharField(label='Nowe hasło', max_length=64, widget=forms.PasswordInput())
    password_repeat = forms.CharField(label='Powtórz hasło', max_length=64, widget=forms.PasswordInput())

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
            'message': forms.Textarea(attrs={'rows':4}),
        }

    def __init__(self, *args, **kwargs):
        
        room = kwargs.pop('room')
        date = kwargs.pop('date')

        super().__init__(*args, **kwargs)
        self.fields['start_date'].initial = date
        self.fields['end_date'].initial = date
        self.fields['room'].initial = room
        room = Room.objects.get(id=room)
        date = change_day_to_date(date)
        prev_reservation = Reservation.objects.filter(room=room, end_date__lt=date).order_by('-end_date').first()
        next_reservation = Reservation.objects.filter(room=room, start_date__gt=date).order_by('start_date').first()
        one_day = datetime.timedelta(days=1)
        
        if prev_reservation:
            self.fields['start_date'].widget.attrs['min'] = prev_reservation.end_date + one_day
            self.fields['end_date'].widget.attrs['min'] = prev_reservation.end_date + one_day
            
        if next_reservation:
            self.fields['start_date'].widget.attrs['max'] = next_reservation.start_date - one_day
            self.fields['end_date'].widget.attrs['max'] = next_reservation.start_date - one_day

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
            'message': forms.Textarea(attrs={'rows':4}),
        }
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        prev_reservation = Reservation.objects.filter(
            Q (room=self.instance.room, end_date__lt=self.instance.start_date) 
            | Q (patient=self.instance.patient, end_date__lt=self.instance.start_date)
        ).order_by('-end_date').first()
        next_reservation = Reservation.objects.filter(
            Q (room=self.instance.room, start_date__gt=self.instance.end_date) 
            | Q (patient=self.instance.patient, start_date__gt=self.instance.end_date)
        ).order_by('start_date').first()
        one_day = datetime.timedelta(days=1)

        if prev_reservation:
            self.fields['start_date'].widget.attrs['min'] = prev_reservation.end_date + one_day
            self.fields['end_date'].widget.attrs['min'] = prev_reservation.end_date + one_day
        
        if next_reservation:
            self.fields['start_date'].widget.attrs['max'] = next_reservation.start_date - one_day
            self.fields['end_date'].widget.attrs['max'] = next_reservation.start_date - one_day

    def clean(self):
        
        cleaned_data = super().clean()

        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']
        prev_reservation = Reservation.objects.filter(
            patient=self.instance.patient,
            end_date__range=(start_date, self.instance.start_date)
            ).order_by('-end_date').first()
        next_reservation = Reservation.objects.filter(
            patient=self.instance.patient,
            start_date__range=(self.instance.end_date, end_date)
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


class TimetableAddForm(forms.ModelForm):
    
    class Meta:
        model = Timetable
        fields = ['patient', 'employee', 'day_timetable', 'hour_timetable', 'reservation']


class TimetableUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Timetable
        fields = ['employee', 'hour_timetable']


class ContactForm(forms.Form):

    subject = forms.CharField(label='Temat', max_length=64)
    first_name = forms.CharField(label='Imię', max_length=64)
    last_name = forms.CharField(label='Nazwisko', max_length=64)
    email = forms.CharField(label='Email', widget=forms.EmailInput(), validators=[EmailValidator()])
    phone = forms.CharField(label='Telefon (+48...)', validators=[validate_phone])
    message = forms.CharField(label='Wiadomość', widget=forms.Textarea(attrs={'rows':5}))
