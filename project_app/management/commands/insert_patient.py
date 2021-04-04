from django.core.management import BaseCommand
from project_app.models import User
from project_app.management.commands_data.patient_data import change_patient


PATIENT_LIST = change_patient()


def insert_patient():
    i = 100
    for first_name, last_name in PATIENT_LIST:
        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=f'{first_name.lower()}{last_name[0].lower()}@onet.pl',
            phone='667345' + str(i),
            password=f'{last_name}_123',
            status=3
        )
        i += 1


class Command(BaseCommand):
    help = "Insert recipe data to database."

    def handle(self, *args, **kwargs):
        insert_patient()
        print("Data load successfully!")
