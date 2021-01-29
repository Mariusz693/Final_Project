from django.db import models
from django.contrib.auth.models import AbstractUser, User, Permission


HOUR_CHOICES = (
    (1, '8:00 - 11:00'),
    (2, '11:00 - 14:00'),
    (3, '14:00 - 17:00')
)


class MyUser(AbstractUser):
    STATUS_CHOICE = (
        (1, 'Administrator'),
        (2, 'Rehabilitant'),
        (3, 'Pacjent')
    )
    tel_number = models.CharField(max_length=9)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=3)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def set_permissions(self):
        if self.status == 1:
            self.user_permissions.set(
                list(Permission.objects.filter(codename__icontains='myuser')) +
                list(Permission.objects.filter(codename__icontains='room')) +
                list(Permission.objects.filter(codename__icontains='reservation')) +
                list(Permission.objects.filter(codename__icontains='timetable'))
            )
        if self.status == 2:
            self.user_permissions.set((
                    Permission.objects.get(codename__icontains='change_myuser'),
                    Permission.objects.get(codename__icontains='view_myuser'),
                    Permission.objects.get(codename__icontains='view_timetable')
                )
            )
        if self.status == 3:
            self.user_permissions.set((
                    Permission.objects.get(codename__icontains='change_myuser'),
                    Permission.objects.get(codename__icontains='view_myuser'),
                    Permission.objects.get(codename__icontains='view_reservation'),
                    Permission.objects.get(codename__icontains='view_timetable')
                )
            )


class Room(models.Model):
    room_number = models.SmallIntegerField(unique=True)

    def __str__(self):
        return f'Pokój nr {self.room_number}'


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_reservation = models.DateField()
    end_reservation = models.DateField()
    message = models.TextField(null=True)
    patient = models.ForeignKey(MyUser, on_delete=models.CASCADE)


class Timetable(models.Model):
    patient = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='patient_timetable')
    employee = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='employee_timetable')
    day_timetable = models.DateField()
    hour_timetable = models.SmallIntegerField(choices=HOUR_CHOICES)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('day_timetable', 'patient')
