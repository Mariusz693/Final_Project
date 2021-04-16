import datetime
import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import View, FormView, DeleteView, CreateView, UpdateView
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate

from .models import User, Room, Reservation, Timetable, UserUniqueToken, HOUR_CHOICES
from .forms import UserLoginForm, UserPasswordForm, PasswordSetForm, PasswordResetForm, ReservationAddForm
from .function import generate_list, generate_month, generate_week_timetable, change_day_to_date, set_day_look, \
     generate_week_user


class IndexView(View):
    """
    Return base page
    """
    def get(self, request):

        return render(
            request,
            'index.html'
        )


class UserLoginView(FormView):
    """
    Return form to login by admin, patient or employee
    """
    form_class = UserLoginForm
    template_name = 'user_login.html'

    def get_success_url(self):
    	
        if self.request.GET.get('next'):

            return str(self.request.GET.get('next'))

        return reverse_lazy('index')

    def form_valid(self, form):

        user = form.authenticate_user()
        
        if user:
        
            login(self.request, user)

        return super().form_valid(form)


class UserLogoutView(View):
    """
    Return logout view
    """
    def get(self, request):

        if self.request.user.is_authenticated:
            
            logout(request)

        return redirect('index')


class PatientListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Return a list of all patient sorted by last name, patient currently in the middle, or last name search results
    Only for user with status admin
    """
    def test_func(self):

        return self.request.user.status == 1

    def get(self, request):

        option_sorted = request.GET.get('sorted')
        option_search = request.GET.get('search')
        if option_sorted == '1':
            today_is = datetime.date.today()
            reservations = Reservation.objects.filter(
                start_reservation__lte=today_is,
                end_reservation__gte=today_is
            ).order_by('room')
            user_list = []
            for reservation in reservations:
                reservation.patient.room = reservation.room.room_number
                user_list.append(reservation.patient)
            message = 2
        elif option_search:
            user_list = User.objects.filter(status=3, last_name__icontains=option_search).order_by('last_name')
            message = option_search
        else:
            user_list = User.objects.filter(status=3).order_by('last_name')
            for i, patient in enumerate(user_list):
                patient.counter = i + 1
            paginator = Paginator(user_list, 12)
            page = request.GET.get('page')
            user_list = paginator.get_page(page)
            message = 1
        
        return render(
            request,
            'user_list.html',
            context={'user_list': user_list, 'message': message}
        )


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Return a list of all employee sorted by last name
    Only for user with status admin
    """
    def test_func(self):
        
        return self.request.user.status == 1

    def get(self, request):

        user_list = User.objects.filter(status=2).order_by('last_name')
        
        return render(
            request,
            'user_list.html',
            context={'user_list': user_list}
        )


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Return the add person form view, with the choice of patient or employee
    Only for user with status admin
    """
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone', 'status']
    template_name = 'user_add.html'

    def test_func(self):
        
        return self.request.user.status == 1

    def form_valid(self, form):
        
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            phone=form.cleaned_data['phone'],
            status=int(form.cleaned_data['status']),
            is_active=False
        )
        new_token = UserUniqueToken.objects.create(user=user)
        send_mail(
            subject='Rejestracja konta',
            message=f'''Twoje konto zostało utworzone w naszym serwisie, twój link do aktywacji konta:
                {self.request.get_host()}{reverse("set-password")}?token={new_token.token}''',
            from_email=self.request.user.email,
            recipient_list=[user.email],
        )

        if user.status == 2:
            success_url = reverse_lazy('employee-list')
    
        elif user.status == 3:    
            success_url = reverse_lazy('patient-list')
        
        else:
            success_url = reverse_lazy('index')

        return HttpResponseRedirect(success_url)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    Return the delete person form view, patient or employee
    Only for user with status admin
    """
    model = User
    template_name = 'user_delete.html'

    def get_object(self):

        if self.request.user.status == 1 and self.request.GET.get('user_id'):
        
            return get_object_or_404(User, id=self.request.GET.get('user_id'))
        
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        
        user = self.get_object()

        if user.status == 1 and User.objects.filter(status=1).count() == 1:
            
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Nie można usunąć ostatniego administratora !!!')
            
            return render(request, template_name=self.template_name)
        
        if request.user.id != user.id:

            if user.status == 2:
                success_url = reverse_lazy('employee-list')
            
            else:
                success_url = reverse_lazy('patient-list')
        
        else:
            success_url = reverse_lazy('index')

        user.delete()

        return HttpResponseRedirect(success_url)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Return the edit person form view of patient or employee
    All user
    """
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone']
    template_name = 'user_edit.html'
    
    def get_object(self):
       
        return self.request.user

    def get_success_url(self):
    	
        return reverse_lazy('user-details')
    
    
class UserDetailsView(LoginRequiredMixin, View):
    """
    Return the view of details patient, employee or admin
    All user
    """
    def get(self, request):

        user = User.objects.get(id=request.user.id)

        return render(
            request,
            'user_details.html',
            context={'user': user}
        )


class UserPasswordView(LoginRequiredMixin, FormView):
    """
    Return the change password form view of patient, employee or admin
    All user
    """    
    form_class = UserPasswordForm
    template_name = 'user_password.html'
    success_url = reverse_lazy('login')

    def get_initial(self):
        
        initial = super().get_initial()
        initial['email'] = self.request.user.email
        
        return initial

    def form_valid(self, form):
    
        user = self.request.user
        password = form.cleaned_data['password_new']
        user.set_password(password)
        user.save()

        logout(self.request)
    
        return super().form_valid(form)


class PasswordSetView(FormView):
    """
    Return the set password form view of patient, employee or admin
    All user
    """    
    form_class = PasswordSetForm
    template_name = 'set_password.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):

        token = self.request.GET.get('token')    
        user_unique_token = get_object_or_404(UserUniqueToken, token=token)
        user = user_unique_token.user

        if user.is_active == False:
            user.is_active = True
        
        password = form.cleaned_data['password_new']
        user.set_password(password)
        user.save()
        user_unique_token.delete()

        return super().form_valid(form)



class PasswordResetView(FormView):

    form_class = PasswordResetForm
    template_name = 'reset_password.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):

        user = User.objects.get(email=form.cleaned_data['email'])
        new_token = UserUniqueToken.objects.create(user=user)

        send_mail(
            subject='Resetowanie hasla',
            message=f'''Twój link do ustawienia nowego hasła:
                {self.request.get_host()}{reverse("set-password")}?token={new_token.token}''',
            from_email='webmaster@localhost',
            recipient_list=[form.cleaned_data['email']],
        )

        return super().form_valid(form)


class ReservationView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Return the reservation patient view
    Only for user with status admin
    """
    def test_func(self):
        
        return self.request.user.status == 1

    def get(self, request):

        month_list = generate_list()
        month_look = request.GET.get('month_look')
        selected_date = change_day_to_date(month_look)
        index_month = month_list.index(selected_date)
        change_month = [
            month_list[index_month-1] if index_month > 0 else None,
            month_list[index_month+1] if index_month < len(month_list) - 1 else None,
        ]
        selected_month_list = generate_month(selected_date)
        selected_month_len = len(selected_month_list[1])
        day_list = selected_month_list[2]
        month_day_start = day_list[0]
        month_day_end = day_list[-1]
        max_date = month_list[-1]
        min_date = month_list[0]
        rooms = Room.objects.all()
        for room in rooms:
            reservation_all = room.reservation_set.filter(
                start_reservation__lte=month_day_end,
                end_reservation__gte=month_day_start
            ).order_by('start_reservation')
            result_table = []
            counter = 0
            for reservation in reservation_all:
                start_reservation = reservation.start_reservation
                end_reservation = reservation.end_reservation
                if (start_reservation - month_day_start).days <= 0:
                    start_reservation = month_day_start
                else:
                    free_time = day_list.index(start_reservation) - counter
                    if free_time:
                        prev_reservation = room.reservation_set.filter(
                            end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                        next_reservation = room.reservation_set.filter(
                            start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                        result_table.append([
                            False,
                            free_time,
                            prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date,
                            next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date
                        ])
                        counter += free_time
                if (end_reservation - month_day_end).days > 0:
                    end_reservation = month_day_end
                during_reservation = (end_reservation - start_reservation).days + 1
                result_table.append([True, during_reservation, reservation])
                counter += during_reservation
            counter = 0
            for item in result_table:
                counter += item[1]
            free_time = selected_month_len - counter
            if free_time:
                prev_reservation = room.reservation_set.filter(
                    end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                next_reservation = room.reservation_set.filter(
                    start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                result_table.append([
                    False,
                    free_time,
                    prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date,
                    next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date
                ])
            room.reserve = result_table

        return render(
                request,
                'reservation.html',
                context={
                    'selected_date': selected_date,
                    'change_month': change_month,
                    'month_list': month_list,
                    'selected_month_list': selected_month_list,
                    'rooms': rooms
                }
            )

class ReservationAddView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    Return the add reservation view
    Only for user with status admin
    """
    form_class = ReservationAddForm
    template_name = 'reservation_add.html'
    
    def test_func(self):
        
        return self.request.user.status == 1

    def get_success_url(self):
    
        selected_month = self.request.GET.get('selected_month')
        
        return f'{reverse("reservation")}?month_look={selected_month}'
    
    def get_initial(self):
        
        initial = super().get_initial()
        
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        room_id = self.request.GET.get('room')
        month_start = self.request.GET.get('month_start')
        month_end = self.request.GET.get('month_end')
        
        initial.update({
            'room': Room.objects.get(room_number=room_id),
            'start_reservation': month_start if month_start > start else start,
            'end_reservation': month_end if month_end < end else end,
        })

        return initial
    
    def get_form_kwargs(self):
        
        kwargs = super().get_form_kwargs()
        
        kwargs.update({
            'start_date': self.request.GET.get('start'),
            'end_date': self.request.GET.get('end')
        })
        
        return kwargs

    def form_valid(self, form):

        form.save()

        return super().form_valid(form)


# class ReservationEditView(LoginRequiredMixin, UserPassesTestMixin, View):
#     """
#     Return the edit reservation view
#     Only for user with status admin
#     """
#     def test_func(self):
#         return self.request.user.status == 1

#     def get(self, request, id_reservation):

#         reservation = Reservation.objects.get(id=id_reservation)
#         room = reservation.room
#         prev_reservation = room.reservation_set.filter(
#             end_reservation__lte=reservation.start_reservation).order_by('-end_reservation').first()
#         next_reservation = room.reservation_set.filter(
#             start_reservation__gte=reservation.end_reservation).order_by('start_reservation').first()
#         month_list = generate_list()
#         max_date = month_list[-1][0]
#         min_date = datetime.date.today()
#         start = prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date
#         start = str(start)
#         end = next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date
#         end = str(end)
#         reservation.start_reservation_change = str(reservation.start_reservation)
#         reservation.end_reservation_change = str(reservation.end_reservation)
#         patient_list = MyUser.objects.filter(status=3)

#         return render(
#             request,
#             'reservation_form.html',
#             context={'room': room, 'reservation': reservation, 'start': start, 'end': end, 'patient_list': patient_list}
#         )

#     def post(self, request, id_reservation):

#         reservation = Reservation.objects.get(id=id_reservation)
#         start_reservation = request.POST.get('start_reservation')
#         end_reservation = request.POST.get('end_reservation')
#         patient_id = request.POST.get('patient_id')
#         room_id = request.POST.get('room_id')
#         message = request.POST.get('message')
#         if start_reservation and end_reservation and patient_id and room_id:
#             room = Room.objects.get(id=room_id)
#             patient = MyUser.objects.get(id=patient_id)

#             if start_reservation > end_reservation:
#                 start = request.POST.get('start')
#                 end = request.POST.get('end')
#                 patient_list = MyUser.objects.filter(status=3)
#                 reservation.start_reservation_change = str(reservation.start_reservation)
#                 reservation.end_reservation_change = str(reservation.end_reservation)

#                 return render(
#                     request,
#                     'reservation_form.html',
#                     context={
#                         'room': room,
#                         'reservation': reservation,
#                         'start': start,
#                         'end': end,
#                         'patient_list': patient_list,
#                         'message': 'Błądnie wpisana data'
#                     }
#                 )

#             reservation_end = Reservation.objects.filter(
#                 patient=patient,
#                 end_reservation__range=(start_reservation, end_reservation)
#             )
#             reservation_start = Reservation.objects.filter(
#                 patient=patient,
#                 start_reservation__range=(start_reservation, end_reservation)
#             )
#             reservation_during = Reservation.objects.filter(
#                 patient=patient,
#                 start_reservation__lte=start_reservation,
#                 end_reservation__gte=end_reservation
#             )

#             if reservation_end or reservation_start or reservation_during:
#                 start = request.POST.get('start')
#                 end = request.POST.get('end')
#                 patient_list = MyUser.objects.filter(status=3)
#                 reservation.start_reservation_change = str(reservation.start_reservation)
#                 reservation.end_reservation_change = str(reservation.end_reservation)

#                 return render(
#                     self.request,
#                     'reservation_form.html',
#                     context={
#                         'room': room,
#                         'reservation': reservation,
#                         'start': start,
#                         'end': end,
#                         'patient_list': patient_list,
#                         'message': 'Pacjent ma już zarezerwowany pobyt w tym terminie hhh'
#                     }
#                 )

#             reservation.start_reservation = start_reservation
#             reservation.end_reservation = end_reservation
#             reservation.patient = patient
#             reservation.message = message
#             reservation.save()
#             timetables = reservation.timetable_set.filter(day_timetable__lte=reservation.start_reservation)
#             if timetables:
#                 for i in range(len(timetables)):
#                     timetables[i].delete()
#             timetables = reservation.timetable_set.filter(day_timetable__gte=reservation.end_reservation)
#             if timetables:
#                 for i in range(len(timetables)):
#                     timetables[i].delete()

#         return redirect('/reservation/?month_look=0')


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Return the delete reservation view
    Only for user with status admin
    """
    model = Reservation
    template_name = 'reservation_delete.html'
    
    def test_func(self):

        return self.request.user.status == 1

    def get_success_url(self):
    
        selected_month = self.request.GET.get('selected_month')
        
        return f'{reverse("reservation")}?month_look={selected_month}'



# @method_decorator(csrf_exempt, name='dispatch')
# class TimetableView(LoginRequiredMixin, UserPassesTestMixin, View):
#     """
#     Return the view where user may add or delete timetable for patient currently in the middle
#     Only for user with status admin
#     """
#     def test_func(self):
#         return self.request.user.status == 1

#     def get(self, request):

#         day_look = request.GET.get('day_look')
#         if day_look == '0':
#             day_look = set_day_look()
#         day_look_date = change_day_to_data(day_look)
#         all_week = generate_week_timetable(day_look_date)
#         employee_list = MyUser.objects.filter(status=2)
#         reservations = Reservation.objects.filter(
#             start_reservation__lte=day_look_date,
#             end_reservation__gte=day_look_date
#         )
#         patient_list = []
#         for reservation in reservations:
#             patient = reservation.patient
#             patient.reservation_id = reservation.id
#             patient_list.append(patient)
#         timetables = Timetable.objects.filter(day_timetable=day_look_date)
#         patient_free_list = []
#         for patient in patient_list:
#             if patient not in [timetable.patient for timetable in timetables]:
#                 patient_free_list.append(patient)

#         timetable_day = []
#         for i, employee in enumerate(employee_list):
#             timetable_day.append([employee, []])
#             for j in range(1, 4):
#                 timetable_day[i][1].append(timetables.filter(employee=employee, hour_timetable=j).first())

#         return render(
#             request,
#             'timetable.html',
#             context={
#                 'patient_free_list': patient_free_list,
#                 'all_week': all_week,
#                 'timetable_day': timetable_day,
#                 'day_look': day_look
#             },
#         )

#     def post(self, request):

#         data = json.loads(request.body.decode())
#         employee_id = int(data['employee_id'])
#         patient_id = int(data['patient_id'])
#         reservation_id = int(data['reservation_id'])
#         hour = int(data['hour'])
#         date = data['date']
#         employee = MyUser.objects.get(id=employee_id)
#         patient = MyUser.objects.get(id=patient_id)
#         reservation = Reservation.objects.get(id=reservation_id)
#         timetable, created = Timetable.objects.update_or_create(
#             patient=patient, day_timetable=date,
#             defaults={
#                 'patient': patient,
#                 'employee': employee,
#                 'day_timetable': date,
#                 'hour_timetable': hour,
#                 'reservation': reservation
#             }
#         )

#         return HttpResponse(timetable.id)

#     def delete(self, request):

#         data = json.loads(request.body.decode())
#         timetable_id = data['timetable_id']
#         timetable = Timetable.objects.get(id=timetable_id)
#         timetable.delete()

#         return HttpResponse('OK')


# class TimetableUserView(LoginRequiredMixin, View):
#     """
#     Return view of the timetable for current user (patient or employee)
#     All user
#     """
#     def get(self, request, id_my_user):

#         if request.user.status != 1 and request.user.id != id_my_user:
#             return redirect('index')

#         my_user = MyUser.objects.get(id=id_my_user)

#         week_look = request.GET.get('week_look')
#         if week_look == '0':
#             week_look = set_day_look()
#         week_look_data = change_day_to_data(week_look)
#         all_week = generate_week_user(week_look_data)
#         timetable_week = [[hour[1]] for hour in HOUR_CHOICES]
#         for i in range(3):
#             for j in range(5):
#                 item = None
#                 if my_user.status == 3:
#                     timetable = Timetable.objects.filter(patient=my_user, day_timetable=all_week[1][j],
#                                                          hour_timetable=i+1).first()
#                     if timetable:
#                         item = timetable.employee
#                 elif my_user.status == 2:
#                     timetable = Timetable.objects.filter(employee=my_user, day_timetable=all_week[1][j],
#                                                          hour_timetable=i + 1).first()
#                     if timetable:
#                         item = timetable.patient
#                 timetable_week[i].append(item)

#         return render(
#             request,
#             'timetable_user.html',
#             context={
#                 'my_user': my_user,
#                 'all_week': all_week,
#                 'timetable_week': timetable_week,
#             }
#         )


# class ReservationUserView(LoginRequiredMixin, View):
#     """
#     Return view of the reservation for current patient
#     All user
#     """
#     def get(self, request, id_my_user):

#         if request.user.status != 1 and request.user.id != id_my_user:
#             return redirect('index')

#         my_user = MyUser.objects.get(id=id_my_user)
#         today = datetime.date.today()
#         reservations = Reservation.objects.filter(patient=my_user, end_reservation__gte=today)\
#             .order_by('start_reservation')
#         for i, reservation in enumerate(reservations):
#             reservation.counter = i + 1

#         reservations_prev = Reservation.objects.filter(patient=my_user, end_reservation__lte=today)\
#             .order_by('start_reservation')
#         for i, reservation in enumerate(reservations_prev):
#             reservation.counter = i + 1

#         return render(
#             request,
#             'reservation_user.html',
#             context={
#                 'my_user': my_user,
#                 'reservations': reservations,
#                 'reservations_prev': reservations_prev,
#             }
#         )
