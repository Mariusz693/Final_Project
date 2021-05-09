import uuid

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from .managers import CustomUserManager
from .validators import validate_tel_number

HOUR_CHOICES = (
    (1, '8:00 - 11:00'),
    (2, '11:00 - 14:00'),
    (3, '14:00 - 17:00')
)

STATUS_CHOICE = (
    (1, 'Administrator'),
    (2, 'Rehabilitant'),
    (3, 'Pacjent')
)

class User(AbstractUser):
    
    username = None
    first_name = models.CharField(verbose_name='Imię', max_length=64)
    last_name = models.CharField(verbose_name='Nazwisko', max_length=64)
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    phone = models.CharField(verbose_name='Telefon (+48...)', max_length=9, validators=[validate_tel_number])
    status = models.SmallIntegerField(verbose_name='Status', choices=STATUS_CHOICE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def delete(self, *args, **kwargs):
        
        if self.status == 1 and self.__class__._default_manager.filter(status=1).count() < 2:
        
            raise ValidationError('Nie można usunąć ostatniego administratora !!!')

        super().delete(*args, **kwargs)

        
class Room(models.Model):
    
    room_number = models.SmallIntegerField(verbose_name='Pokój', unique=True)

    def __str__(self):
        return str(self.room_number)


class Reservation(models.Model):
    
    room = models.ForeignKey(Room, verbose_name='Pokój', on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Data rozpoczęcia')
    end_date = models.DateField(verbose_name='Data zakończenia')
    message = models.TextField(verbose_name='Notatka', blank=True)
    patient = models.ForeignKey(User, limit_choices_to={'status': 3, 'is_active': True}, verbose_name='Pacjent', on_delete=models.CASCADE)

    @classmethod
    def from_db(cls, db, field_names, values):
    
        instance = super().from_db(db, field_names, values)
        instance._loaded_values = dict(zip(field_names, values))
        
        return instance

    def validate_unique(self, *args, **kwargs):
        
        super().validate_unique(*args, **kwargs)

        if self.end_date < self.start_date:
            raise ValidationError({NON_FIELD_ERRORS: 'Data zakończenia musi być poźniej od daty rozpoczęcia'})

        if self._state.adding:
            reservation_room = self.__class__._default_manager.filter(
                Q(room=self.room, end_date__range=(self.start_date, self.end_date))
                |Q(room=self.room, start_date__range=(self.start_date, self.end_date))
                |Q(room=self.room, start_date__lte=self.start_date, end_date__gte=self.end_date)
            ).first()

            if reservation_room:
                raise ValidationError({NON_FIELD_ERRORS: 'Pokój jest już zarezerwowany w tym terminie, sprawdź terminarz'})
        else:
            reservation_room = self.__class__._default_manager.filter(
                Q(room=self.room, end_date__range=(self.start_date, self._loaded_values['start_date']))
                |Q(room=self.room, start_date__range=(self._loaded_values['end_date'], self.end_date))
            ).first()

            if reservation_room:                
                raise ValidationError({NON_FIELD_ERRORS: 'Pokój jest już zarezerwowany w tym terminie, sprawdź terminarz'})
        

class Timetable(models.Model):
    
    patient = models.ForeignKey(User, limit_choices_to={'status': 3, 'is_active': True}, verbose_name='Pacjent', on_delete=models.CASCADE, related_name='patient_timetable')
    employee = models.ForeignKey(User, limit_choices_to={'status': 2, 'is_active': True}, verbose_name='Rehabilitant', on_delete=models.CASCADE, related_name='employee_timetable')
    day_timetable = models.DateField(verbose_name='Dzień')
    hour_timetable = models.SmallIntegerField(choices=HOUR_CHOICES, verbose_name='Godzina')
    reservation = models.ForeignKey(Reservation, verbose_name='Rezerwacja', on_delete=models.CASCADE)

    def validate_unique(self, *args, **kwargs):
        
        super().validate_unique(*args, **kwargs)

        timetable = self.__class__._default_manager.filter(
            employee=self.employee,
            day_timetable=self.day_timetable,
            hour_timetable=self.hour_timetable
        ).first()

        if timetable:                
            raise ValidationError({NON_FIELD_ERRORS: 'Grafik zajety'})

class UserUniqueToken(models.Model):

    user = models.ForeignKey(User, verbose_name='Użytkownik', on_delete=models.CASCADE)
    token = models.UUIDField(primary_key=True, verbose_name='Token', default=uuid.uuid4, editable=False)
