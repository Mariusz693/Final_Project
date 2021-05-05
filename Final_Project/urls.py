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
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('patient_list/', views.PatientListView.as_view(), name='patient-list'),
    path('employee_list/', views.EmployeeListView.as_view(), name='employee-list'),
    path('user_add/', views.UserCreateView.as_view(), name='user-add'),
    path('user_update/', views.UserUpdateView.as_view(), name='user-update'),
    path('user_details/', views.UserDetailsView.as_view(), name='user-details'),
    path('user_delete/', views.UserDeleteView.as_view(), name='user-delete'),
    path('user_password_update/', views.UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('user_password_set/', views.UserPasswordSetView.as_view(), name='user-password-set'),
    path('user_password_reset/', views.UserPasswordResetView.as_view(), name='user-password-reset'),
    path('reservation/', views.ReservationView.as_view(), name='reservation'),
    path('reservation_add/', views.ReservationAddView.as_view(), name='reservation-add'),
    path('reservation_update/<int:pk>/', views.ReservationUpdateView.as_view(), name='reservation-update'),
    path('reservation_delete/<int:pk>/', views.ReservationDeleteView.as_view(), name='reservation-delete'),
    path('reservation/<int:pk>/', views.UserReservationView.as_view(), name='user-reservation'),
    path('timetable/', views.TimetableView.as_view(), name='timetable'),
    path('timetable/<int:pk>/', views.UserTimetableView.as_view(), name='user-timetable'),
    
    # path('reservation/', views.UserLoginView.as_view(), name='reservation'),
    
    # path('reservation_edit/<int:id_reservation>/', views.UserLoginView.as_view(), name='reservation-edit'),
    # path('timetable/', views.UserLoginView.as_view(), name='timetable'),
    # path('timetable/<int:id_user>/', views.UserLoginView.as_view(), name='timetable-user'),


]
