from django.db import models
from django.contrib.auth.models import AbstractUser, User, Permission


class MyUser(AbstractUser):
    STATUS_CHOICE = (
        (1, 'Administrator'),
        (2, 'Rehabilitant'),
        (3, 'Pacjent')
    )
    tel_number = models.CharField(max_length=9)
    status = models.SmallIntegerField(choices=STATUS_CHOICE, default=3)

    def set_permissions(self):
        if self.status == 1:
            self.user_permissions.set(
                list(Permission.objects.filter(codename__icontains='myuser')) +
                list(Permission.objects.filter(codename__icontains='room')) +
                list(Permission.objects.filter(codename__icontains='reservation'))
            )
        if self.status == 2 or self.status == 3:
            self.user_permissions.set((
                    Permission.objects.get(codename__icontains='delete_myuser'),
                    Permission.objects.get(codename__icontains='change_myuser'),
                    Permission.objects.get(codename__icontains='view_myuser')
                )
            )


class Room(models.Model):
    room_number = models.SmallIntegerField(unique=True)


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_reservation = models.DateField()
    end_reservation = models.DateField()
    message = models.TextField(null=True)
    patient = models.ForeignKey(MyUser, on_delete=models.CASCADE)
