"""Final_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.MyUserLoginView.as_view(), name='login'),
    path('logout/', views.MyUserLogoutView.as_view(), name='logout'),
    path('patient_list/', views.PatientListView.as_view(), name='patient-list'),
    path('employee_list/', views.EmployeeListView.as_view(), name='employee-list'),
    path('my_user_add/', views.MyUserCreateView.as_view(), name='my-user-add'),
    path('my_user_delete/<int:pk>/', views.MyUserDeleteView.as_view(), name='my-user-delete'),
    path('my_user_edit/<int:id_my_user>/', views.MyUserUpdateView.as_view(), name='my-user-edit'),
    path('my_user_details/<int:id_my_user>/', views.MyUserDetailsView.as_view(), name='my-user-details'),
    path('my_user_password/<int:id_my_user>/', views.MyUserPasswordView.as_view(), name='my-user-password'),
    path('reservation/', views.ReservationView.as_view(), name='reservation'),
    path('reservation_add/', views.ReservationAddView.as_view(), name='reservation-add'),
    path('reservation_edit/<int:id_reservation>/', views.ReservationEditView.as_view(), name='reservation-edit'),
    path('reservation_delete/<int:pk>/', views.ReservationDeleteView.as_view(), name='reservation-delete'),
    path('timetable/', views.TimetableView.as_view(), name='timetable'),
    path('timetable/<int:id_my_user>/', views.TimetableUserView.as_view(), name='timetable-user'),
    path('reservation/<int:id_my_user>/', views.ReservationUserView.as_view(), name='reservation-patient'),
]
