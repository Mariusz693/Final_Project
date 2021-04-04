import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager

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
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    phone = models.CharField(max_length=9, blank=True)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=3)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Room(models.Model):
    
    room_number = models.SmallIntegerField(unique=True)

    def __str__(self):
        return f'Pokój nr {self.room_number}'


class Reservation(models.Model):
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_reservation = models.DateField()
    end_reservation = models.DateField()
    message = models.TextField(null=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)


class Timetable(models.Model):
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_timetable')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_timetable')
    day_timetable = models.DateField()
    hour_timetable = models.SmallIntegerField(choices=HOUR_CHOICES)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('day_timetable', 'patient')


class UserUniqueToken(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)