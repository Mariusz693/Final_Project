import pytest
from project_app.models import MyUser, Reservation, Timetable


@pytest.mark.django_db
def test_patient_add(client, user_admin):

    client.force_login(user=user_admin, backend=None)
    assert MyUser.objects.filter(status=3).count() == 0  # Sprawdzam stan bazy osób ze statusem pacjent
    post_data = {
        'nick': 'Artur_Dudy',
        'first_name': 'Artur',
        'last_name': 'Duda',
        'email': 'ad@onet.pl',
        'tel_number': '689346976',
        'status': 3,
        'password': 'Dudy123',
        'repeat_password': 'Dudy123'
    }
    response = client.post('/my_user_add/', post_data)
    assert MyUser.objects.filter(status=3).count() == 1
    assert response.status_code == 302
    client.logout()


@pytest.mark.django_db
def test_employee_add(client, user_admin):

    client.force_login(user=user_admin, backend=None)
    assert MyUser.objects.filter(status=2).count() == 0  # Sprawdzam stan bazy
    post_data = {
        'nick': 'Artur_Dudy',
        'first_name': 'Artur',
        'last_name': 'Duda',
        'email': 'ad@onet.pl',
        'tel_number': '689346976',
        'status': 2,
        'password': 'Dudy123',
        'repeat_password': 'Dudy123'
    }
    response = client.post('/my_user_add/', post_data)
    assert MyUser.objects.filter(status=2).count() == 1
    assert response.status_code == 302
    client.logout()


@pytest.mark.django_db
def test_patient_delete_admin(client, user_admin, patient_list):

    assert MyUser.objects.filter(status=3).count() == 10
    client.force_login(user=user_admin, backend=None)
    response = client.post(f'/my_user_delete/{patient_list[9].id}/')
    assert MyUser.objects.filter(status=3).count() == 9
    assert response.status_code == 302
    client.logout()


@pytest.mark.django_db
def test_patient_delete_patient(client, user_patient, patient_list):

    assert MyUser.objects.filter(status=3).count() == 10
    client.force_login(user=user_patient, backend=None)
    response = client.get(f'/my_user_delete/{patient_list[8].id}/')
    assert MyUser.objects.filter(status=3).count() == 10
    client.logout()


@pytest.mark.django_db
def test_patient_delete_employee(client, user_employee, patient_list):

    assert MyUser.objects.filter(status=3).count() == 10
    client.force_login(user=user_employee, backend=None)
    response = client.get(f'/my_user_delete/{patient_list[8].id}/')
    assert MyUser.objects.filter(status=3).count() == 10
    client.logout()


@pytest.mark.django_db
def test_patient_edit(client, user_admin, patient):

    client.force_login(user=user_admin, backend=None)
    assert MyUser.objects.filter(status=3).count() == 1  # Sprawdzam stan bazy
    response = client.get(f'/my_user_edit/{patient.id}/')
    assert response.status_code == 200
    post_data = {
        'nick': 'Artur_Duda',
        'email': 'ad@onet.pl',
        'tel_number': '689746976'
    }
    client.force_login(user=user_admin, backend=None)
    response = client.post(f'/my_user_edit/{patient.id}/', post_data)
    assert response.status_code == 302
    assert MyUser.objects.filter(status=3).count() == 1
    patient_obj = MyUser.objects.get(id=patient.id)
    assert patient_obj.username == post_data['nick']
    assert patient_obj.email == post_data['email']
    assert patient_obj.tel_number == post_data['tel_number']
    client.logout()


@pytest.mark.django_db
def test_patient_list(client, user_admin, patient_list):

    client.force_login(user=user_admin, backend=None)
    response = client.get('/patient_list/')
    assert response.status_code == 200
    assert response.context['my_user_list'][0] == patient_list[0]
    assert response.context['my_user_list'][1] == patient_list[1]
    assert response.context['my_user_list'][2] == patient_list[2]
    assert response.context['my_user_list'][3] == patient_list[3]
    assert response.context['my_user_list'][4] == patient_list[4]
    assert response.context['my_user_list'][5] == patient_list[5]
    assert response.context['my_user_list'][6] == patient_list[6]
    assert response.context['my_user_list'][7] == patient_list[7]
    assert response.context['my_user_list'][8] == patient_list[8]
    assert response.context['my_user_list'][9] == patient_list[9]
    client.logout()


@pytest.mark.django_db
def test_patient_detail(client, user_admin, patient):

    client.force_login(user=user_admin, backend=None)
    response = client.get(f'/my_user_details/{patient.id}/')
    assert response.status_code == 200
    response_context = response.context['my_user']
    assert response_context.username == patient.username
    assert response_context.first_name == patient.first_name
    assert response_context.last_name == patient.last_name
    assert response_context.tel_number == patient.tel_number
    assert response_context.email == patient.email
    assert response_context.status == patient.status
    client.logout()


@pytest.mark.django_db
def test_login(client):
    post_data = {
        'username': 'Admin',
        'password': 'Admin'
    }
    response = client.post('/login/', post_data)
    assert response.status_code == 200
