from django.core.management import BaseCommand
from project_app.models import MyUser
from project_app.management.commands_data.patient_data import change_patient


PATIENT_LIST = change_patient()


def insert_patient():
    i = 100
    for first_name, last_name in PATIENT_LIST:
        new_patient = MyUser.objects.create_user(
            username=f'{first_name}_{last_name}',
            first_name=first_name,
            last_name=last_name,
            email=f'{first_name.lower()}{last_name[0].lower()}@onet.pl',
            tel_number='667345' + str(i),
            password=f'{last_name}123',
            status=3
        )
        new_patient.set_permissions()
        i += 1


class Command(BaseCommand):
    help = "Insert recipe data to database."

    def handle(self, *args, **kwargs):
        insert_patient()
        print("Data load successfully!")
