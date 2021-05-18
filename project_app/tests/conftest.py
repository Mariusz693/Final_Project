import pytest
from random import randint
from django.test import Client
from project_app.models import User, Reservation, Timetable


@pytest.fixture
def client():
    client = Client()

    return client


@pytest.fixture
def admin():

    admin = User.objects.create_user(
        email='admin_fixture@onet.pl', 
        first_name='Admin', 
        last_name='Admin', 
        phone='123456789', 
        status=1,
        password='Admin_123'
        )
    return admin


@pytest.fixture
def patient():

    patient = User.objects.create_user(
        email='patient_fixture@onet.pl', 
        first_name='Patient', 
        last_name='Patient', 
        phone='123456789', 
        status=3,
        password='Patient_123'
        )

    return patient


@pytest.fixture
def employee():

    employee = User.objects.create_user(
        email='employee_fixture@onet.pl', 
        first_name='Employee', 
        last_name='Employee', 
        phone='123456789', 
        status=2,
        password='Employee_123'
        )

    return employee


@pytest.fixture
def patient_list():

    for i in range(8):
        User.objects.create_user(
            first_name='Patient',
            last_name=f'Patient{i}',
            email=f'patient{i}@onet.pl',
            phone='689346976',
            status=3
        )
        
    return User.objects.filter(status=3).order_by('last_name')


@pytest.fixture
def employee_list():

    for i in range(8):
        User.objects.create_user(
            first_name='Employee',
            last_name='Employee',
            email=f'employee{i}@onet.pl',
            phone='689346976',
            status=2
        )
        
    return User.objects.filter(status=2)


@pytest.fixture
def user_list():

    for i in range(30):
        User.objects.create_user(
            first_name='User',
            last_name='User',
            email=f'user{i}@onet.pl',
            phone='689346976',
            status=1 if i < 5 else 2 if i < 10 else 3
        )

    return User.objects.all()
