import pytest
from project_app.models import User, Reservation, Timetable


@pytest.mark.django_db
def test_login(client, admin):
    
    post_data = {
        'email': 'admin_fixture@onet.pl',
        'password': 'Admin_123'
    }
    response = client.post('/login/', post_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_add_by_admin(client, admin):

    client.login(email='admin_fixture@onet.pl', password='Admin_123')
    
    post_data_patient = {
        'first_name': 'User',
        'last_name': 'Patient',
        'email': 'patient@onet.pl',
        'phone': '689346976',
        'status': 3
    }
    assert User.objects.filter(status=3).count() == 0  # check databade
    response = client.post('/user_add/', post_data_patient)
    assert User.objects.filter(status=3).count() == 1
    assert response.status_code == 302
    
    post_data_employee = {
        'first_name': 'User',
        'last_name': 'Employee',
        'email': 'employee@onet.pl',
        'phone': '689346976',
        'status': 2
    }
    assert User.objects.filter(status=2).count() == 0  # Check database
    response = client.post('/user_add/', post_data_employee)
    assert User.objects.filter(status=2).count() == 1
    assert response.status_code == 302
    
    post_data_admin = {
        'first_name': 'User',
        'last_name': 'Admin',
        'email': 'admin@onet.pl',
        'phone': '689346976',
        'status': 1
    }
    assert User.objects.filter(status=1).count() == 1  # Check database
    response = client.post('/user_add/', post_data_admin)
    assert User.objects.filter(status=1).count() == 2
    assert response.status_code == 302
    
    client.logout()


@pytest.mark.django_db
def test_user_add_by_patient(client, patient):

    client.login(email='patient_fixture@onet.pl', password='Patient_123')
    assert User.objects.filter(status=1).count() == 0  # Sprawdzam stan bazy
    post_data = {
        'first_name': 'User',
        'last_name': 'User',
        'email': 'user@onet.pl',
        'phone': '689346976',
        'status': 1,
    }
    response = client.post('/user_add/', post_data)
    assert User.objects.filter(status=1).count() == 0
    assert response.status_code == 403
    client.logout()


@pytest.mark.django_db
def test_user_delete(client, patient, employee):

    client.login(email='patient_fixture@onet.pl', password='Patient_123')
    assert User.objects.filter(status=3).count() == 1
    response = client.post(f'/user_delete/')
    assert User.objects.filter(status=3).count() == 0
    assert response.status_code == 302

    client.login(email='employee_fixture@onet.pl', password='Employee_123')
    assert User.objects.filter(status=2).count() == 1
    response = client.post(f'/user_delete/')
    assert User.objects.filter(status=1).count() == 0
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_delete_by_admin(client, admin, employee_list, patient_list):

    client.login(email='admin_fixture@onet.pl', password='Admin_123')
    assert User.objects.all().count() == 16

    assert User.objects.filter(status=3).count() == 10
    response = client.post(f'/user_delete/?pk={patient_list.first().id}')
    assert User.objects.filter(status=3).count() == 9
    assert response.status_code == 302

    assert User.objects.filter(status=2).count() == 5
    response = client.post(f'/user_delete/?pk={employee_list.first().id}')
    assert User.objects.filter(status=2).count() == 4
    assert response.status_code == 302
    
    assert User.objects.all().count() == 14
    client.logout()


@pytest.mark.django_db
def test_user_admin(client, admin):

    client.login(email='admin_fixture@onet.pl', password='Admin_123')
    assert User.objects.filter(status=1).count() == 1
    response = client.post(f'/user_delete/')
    assert User.objects.filter(status=1).count() == 1
    assert response.status_code == 200
    client.logout()


@pytest.mark.django_db
def test_user_update(client, patient):

    client.login(email='patient_fixture@onet.pl', password='Patient_123')
    post_data = {
        'first_name': 'New_name',
        'last_name': 'New_last_name',
        'email': 'new_email@onet.pl',
        'phone': '689746976'
    }
    response = client.post(f'/user_update/', post_data)
    assert response.status_code == 302
    patient_obj = User.objects.get(id=patient.id)
    assert patient_obj.first_name == post_data['first_name']
    assert patient_obj.last_name == post_data['last_name']
    assert patient_obj.email == post_data['email']
    assert patient_obj.phone == post_data['phone']
    client.logout()


@pytest.mark.django_db
def test_password_update(client, admin):
    
    post_data = {
        'email': 'admin@onet.pl',
        'password_check': 'Admin2',
        'password_new': 'Admin2',
        'password_repeat': 'Admin2'
    }
    client.force_login(user=admin, backend=None)
    response = client.post('/user_password_update/', post_data)
    assert response.status_code == 200


# @pytest.mark.django_db
# def test_patient_list(client, admin, patient_list):

#     client.force_login(user=admin, backend=None)
#     response = client.get('/patient_list/')
#     assert response.status_code == 200
#     assert response.context['object_list'][0] == patient_list[0]
#     assert response.context['object_list'][1] == patient_list[1]
#     assert response.context['object_list'][2] == patient_list[2]
#     assert response.context['object_list'][3] == patient_list[3]
#     assert response.context['object_list'][4] == patient_list[4]
#     assert response.context['object_list'][5] == patient_list[5]
#     assert response.context['object_list'][6] == patient_list[6]
#     assert response.context['object_list'][7] == patient_list[7]
#     client.logout()


# @pytest.mark.django_db
# def test_user_detail(client, admin, patient, employee):

#     client.force_login(user=admin, backend=None)
#     response = client.get(f'/user_details/')
#     assert response.status_code == 200
#     response_context = response.context['object']
#     assert response_context.first_name == admin.first_name
#     assert response_context.last_name == admin.last_name
#     assert response_context.phone == admin.phone
#     assert response_context.email == admin.email
#     assert response_context.status == admin.status
#     client.logout()

#     client.force_login(user=patient, backend=None)
#     response = client.get(f'/user_details/')
#     assert response.status_code == 200
#     response_context = response.context['object']
#     assert response_context.first_name == patient.first_name
#     assert response_context.last_name == patient.last_name
#     assert response_context.phone == patient.phone
#     assert response_context.email == patient.email
#     assert response_context.status == patient.status
#     client.logout()

#     client.force_login(user=employee, backend=None)
#     response = client.get(f'/user_details/')
#     assert response.status_code == 200
#     response_context = response.context['object']
#     assert response_context.first_name == employee.first_name
#     assert response_context.last_name == employee.last_name
#     assert response_context.phone == employee.phone
#     assert response_context.email == employee.email
#     assert response_context.status == employee.status
#     client.logout()
