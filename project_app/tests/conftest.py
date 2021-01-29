import pytest
from django.test import Client
from project_app.models import MyUser, Reservation, Timetable


@pytest.fixture
def client():
    client = Client()

    return client


@pytest.fixture
def user_admin():
    user_admin = MyUser.objects.create_user(username='Admin', email=None, password='Admin', status=1)

    return user_admin


@pytest.fixture
def user_patient():
    user_patient = MyUser.objects.create_user(username='Patient', email=None, password='Patient', status=1)

    return user_patient


@pytest.fixture
def user_employee():
    user_employee = MyUser.objects.create_user(username='Employee', email=None, password='Employee', status=1)

    return user_employee


@pytest.fixture
def patient():
    patient = MyUser.objects.create_user(
        username='Artur_Dudy',
        first_name='Artur',
        last_name='Duda',
        email='ad@onet.pl',
        tel_number='689346976',
        status=3,
        password='Dudy123'
    )

    return patient


@pytest.fixture
def patient_list():
    patient_list = []
    for i in range(10):
        patient = MyUser.objects.create_user(
            username=f'Artur_Dudy_{i+1}',
            first_name='Artur',
            last_name='Duda',
            email='ad@onet.pl',
            tel_number='689346976',
            status=3,
            password='Dudy123'
        )
        patient_list.append(patient)

    return patient_list
