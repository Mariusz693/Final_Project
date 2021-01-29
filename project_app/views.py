import datetime
import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView, DeleteView, View
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from .models import MyUser, Room, Reservation, Timetable, HOUR_CHOICES
from .forms import MyUserLoginForm, MyUserCreateForm, MyUserUpdateForm, MyUserPasswordForm
from .function import generate_list, generate_month, generate_week_timetable, change_day_to_data, set_day_look, \
     generate_week_user


class IndexView(View):
    """

    """

    def get(self, request):

        return render(
            request,
            'index.html'
        )


class MyUserLoginView(FormView):

    form_class = MyUserLoginForm
    template_name = 'my_user_login.html'

    def get_success_url(self):

        if self.request.GET.get('next'):

            return str(self.request.GET.get('next'))

        return '../'

    def form_valid(self, form):

        user = form.authenticate_user()
        if user:
            login(self.request, user)
        else:
            return render(
                self.request,
                'my_user_login.html',
                context={'form': MyUserLoginForm, 'message': 'Błąd logowania'}
            )

        return super(MyUserLoginView, self).form_valid(form)


class MyUserLogoutView(View):

    def get(self, request):
        if self.request.user.is_authenticated:
            logout(request)

        return redirect('index')


class PatientListView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):

        message = 1
        option_sorted = request.GET.get('sorted')
        option_search = request.GET.get('search')
        if option_sorted == '1':
            today_is = datetime.date.today()
            reservations = Reservation.objects.filter(
                start_reservation__lte=today_is,
                end_reservation__gte=today_is
            ).order_by('room')
            my_user_list = []
            for reservation in reservations:
                reservation.patient.room = reservation.room.room_number
                my_user_list.append(reservation.patient)
            message = 2
        elif option_search:
            my_user_list = MyUser.objects.filter(status=3, last_name__icontains=option_search).order_by('last_name')
            for i, patient in enumerate(my_user_list):
                patient.counter = i + 1
                message = option_search
        else:
            my_user_list = MyUser.objects.filter(status=3).order_by('last_name')
            for i, patient in enumerate(my_user_list):
                patient.counter = i + 1
            paginator = Paginator(my_user_list, 12)
            page = request.GET.get('page')
            my_user_list = paginator.get_page(page)

        return render(
            request,
            'my_user_list.html',
            context={'my_user_list': my_user_list, 'message': message}
        )


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):

        my_user_list = MyUser.objects.filter(status=2).order_by('last_name')
        for i, employee in enumerate(my_user_list):
            employee.counter = i + 1

        return render(
            request,
            'my_user_list.html',
            context={'my_user_list': my_user_list}
        )


class MyUserCreateView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):

        form = MyUserCreateForm()

        return render(
            request,
            'my_user_add.html',
            context={'form': form}
        )

    def post(self, request):

        form = MyUserCreateForm(request.POST)
        if form.is_valid():
            nick = form.cleaned_data['nick']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            tel_number = form.cleaned_data['tel_number']
            status = int(form.cleaned_data['status'])
            password = form.cleaned_data['password']
            new_patient = MyUser.objects.create_user(
                username=nick,
                first_name=first_name,
                last_name=last_name,
                email=email,
                tel_number=tel_number,
                password=password,
                status=status
            )

            if status == 2:
                return redirect('employee-list')
            else:
                return redirect('patient-list')

        return render(
            self.request,
            'my_user_add.html',
            context={'form': form, 'message': 'Błąd danych'}
        )


class MyUserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    def test_func(self):
        return self.request.user.status == 1

    model = MyUser
    template_name = 'my_user_delete.html'

    def delete(self, request, *args, **kwargs):
        my_user = self.get_object()

        if my_user.status == 2:
            success_url = '/employee_list/'
        else:
            success_url = '/patient_list/'

        my_user.delete()

        return HttpResponseRedirect(success_url)


class MyUserUpdateView(LoginRequiredMixin, View):

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        form = MyUserUpdateForm(initial={
            'nick': my_user.username,
            'email': my_user.email,
            'tel_number': my_user.tel_number,
        })

        return render(
            request,
            'my_user_edit.html',
            context={'form': form, 'my_user': my_user}
        )

    def post(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        status = my_user.status
        form = MyUserUpdateForm(request.POST)

        if form.is_valid():
            my_user.username = form.cleaned_data['nick']
            my_user.email = form.cleaned_data['email']
            my_user.tel_number = form.cleaned_data['tel_number']

            my_user.save()

            if request.user.status == 1:
                if status == 2:
                    return redirect('employee-list')
                if status == 3:
                    return redirect('patient-list')

            return redirect('my-user-details', my_user.id)

        return render(
            self.request,
            'my_user_edit.html',
            context={'form': form, 'message': 'Błąd danych'}
        )


class MyUserDetailsView(LoginRequiredMixin, View):

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)

        return render(
            request,
            'my_user_details.html',
            context={'my_user': my_user}
        )


class MyUserPasswordView(LoginRequiredMixin, View):

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        form = MyUserPasswordForm()

        return render(
            request,
            'my_user_password.html',
            context={'form': form, 'my_user': my_user}
        )

    def post(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        status = my_user.status
        form = MyUserPasswordForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password']
            my_user.set_password(password)
            my_user.save()

            if request.user.status == 1:
                if status == 2:
                    return redirect('employee-list')

                return redirect('patient-list')

            return redirect('login')

        return render(
            self.request,
            'my_user_edit.html',
            context={'form': form, 'message': 'Błąd danych'}
        )


class ReservationView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):

        month_list = generate_list()
        month_look = request.GET.get('month_look')
        if month_look == '0':
            today = datetime.date.today()
            month_look = str(datetime.date(year=today.year, month=today.month, day=1))
        month_look_data = change_day_to_data(month_look)
        index_month = month_list.index([month_look_data, month_look])
        change_month = [
            month_list[index_month-1][1] if index_month > 0 else None,
            month_list[index_month+1][1] if index_month < len(month_list) - 1 else None,
        ]
        month_look_list = generate_month(month_look_data)
        month_len = len(month_look_list[0]) * 7
        day_list = month_look_list[1]
        month_day_start = day_list[0]
        month_day_end = day_list[-1]
        max_date = month_list[-1][0]
        min_date = month_list[0][0]
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
                    prev_reservation = room.reservation_set.filter(
                        end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                    next_reservation = room.reservation_set.filter(
                        start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                    result_table.append([
                        False,
                        free_time,
                        str(prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date),
                        str(next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date)
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
            free_time = month_len - counter
            if free_time:
                prev_reservation = room.reservation_set.filter(
                    end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                next_reservation = room.reservation_set.filter(
                    start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                result_table.append([
                    False,
                    free_time,
                    str(prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date),
                    str(next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date)
                ])
            room.reserve = result_table

        return render(
                request,
                'reservation.html',
                context={
                    'month_list': month_list,
                    'month_look': month_look_data,
                    'change_month': change_month,
                    'month_look_list': month_look_list,
                    'rooms': rooms,
                }
            )


class ReservationAddView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        room_id = request.GET.get('room')
        room = Room.objects.get(id=room_id)
        patient_list = MyUser.objects.filter(status=3)
        return render(
            request,
            'reservation_form.html',
            context={'room': room, 'start': start, 'end': end, 'patient_list': patient_list}
        )

    def post(self, request):
        start_reservation = request.POST.get('start_reservation')
        end_reservation = request.POST.get('end_reservation')
        patient_id = request.POST.get('patient_id')
        room_id = request.POST.get('room_id')
        message = request.POST.get('message')
        if start_reservation and end_reservation and patient_id and room_id:
            room = Room.objects.get(id=room_id)

            if start_reservation > end_reservation:
                start = request.POST.get('start')
                end = request.POST.get('end')
                patient_list = MyUser.objects.filter(status=3)

                return render(
                    self.request,
                    'reservation_form.html',
                    context={'room': room, 'start': start, 'end': end, 'patient_list': patient_list, 'message': 'Błąd daty'}
                )

            patient = MyUser.objects.get(id=patient_id)
            reservation = Reservation.objects.create(
                patient=patient,
                room=room,
                start_reservation=start_reservation,
                end_reservation=end_reservation,
                message=message
            )

            return redirect('../reservation/?month_look=0')


class ReservationEditView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request, id_reservation):

        reservation = Reservation.objects.get(id=id_reservation)
        room = reservation.room
        prev_reservation = room.reservation_set.filter(
            end_reservation__lte=reservation.start_reservation).order_by('-end_reservation').first()
        next_reservation = room.reservation_set.filter(
            start_reservation__gte=reservation.end_reservation).order_by('start_reservation').first()
        month_list = generate_list()
        max_date = month_list[-1][0]
        min_date = datetime.date.today()
        start = prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date
        start = str(start)
        end = next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date
        end = str(end)
        reservation.start_reservation_change = str(reservation.start_reservation)
        reservation.end_reservation_change = str(reservation.end_reservation)
        patient_list = MyUser.objects.filter(status=3)

        return render(
            request,
            'reservation_form.html',
            context={'room': room, 'reservation': reservation, 'start': start, 'end': end, 'patient_list': patient_list}
        )

    def post(self, request, id_reservation):

        reservation = Reservation.objects.get(id=id_reservation)
        start_reservation = request.POST.get('start_reservation')
        end_reservation = request.POST.get('end_reservation')
        patient_id = request.POST.get('patient_id')
        room_id = request.POST.get('room_id')
        message = request.POST.get('message')
        if start_reservation and end_reservation and patient_id and room_id:
            room = Room.objects.get(id=room_id)
            if start_reservation > end_reservation:
                start = request.POST.get('start')
                end = request.POST.get('end')
                patient_list = MyUser.objects.filter(status=3)
                reservation.start_reservation_change = str(reservation.start_reservation)
                reservation.end_reservation_change = str(reservation.end_reservation)

                return render(
                    request,
                    'reservation_form.html',
                    context={
                        'room': room,
                        'reservation': reservation,
                        'start': start,
                        'end': end,
                        'patient_list': patient_list,
                        'message': 'Błąd daty'
                    }
                )

            patient = MyUser.objects.get(id=patient_id)
            reservation.start_reservation = start_reservation
            reservation.end_reservation = end_reservation
            reservation.patient = patient
            reservation.message = message
            reservation.save()
            timetables = reservation.timetable_set.filter(day_timetable__lte=reservation.start_reservation)
            if timetables:
                for i in range(len(timetables)):
                    timetables[i].delete()
            timetables = reservation.timetable_set.filter(day_timetable__gte=reservation.end_reservation)
            if timetables:
                for i in range(len(timetables)):
                    timetables[i].delete()

        return redirect('/reservation/?month_look=0')


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    def test_func(self):
        return self.request.user.status == 1

    permission_required = 'project_app.delete_reservation'
    model = Reservation
    template_name = 'reservation_delete.html'
    success_url = '/reservation/?month_look=0'


@method_decorator(csrf_exempt, name='dispatch')
class TimetableView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.status == 1

    def get(self, request):

        if request.user.status != 1:
            return redirect('index')

        day_look = request.GET.get('day_look')
        if day_look == '0':
            day_look = set_day_look()
        day_look_date = change_day_to_data(day_look)
        all_week = generate_week_timetable(day_look_date)
        employee_list = MyUser.objects.filter(status=2)
        reservations = Reservation.objects.filter(
            start_reservation__lte=day_look_date,
            end_reservation__gte=day_look_date
        )
        patient_list = []
        for reservation in reservations:
            patient = reservation.patient
            patient.reservation_id = reservation.id
            patient_list.append(patient)
        timetables = Timetable.objects.filter(day_timetable=day_look_date)
        patient_free_list = []
        for patient in patient_list:
            if patient not in [timetable.patient for timetable in timetables]:
                patient_free_list.append(patient)

        timetable_day = []
        for i, employee in enumerate(employee_list):
            timetable_day.append([employee, []])
            for j in range(1, 4):
                timetable_day[i][1].append(timetables.filter(employee=employee, hour_timetable=j).first())

        return render(
            request,
            'timetable.html',
            context={
                'patient_free_list': patient_free_list,
                'all_week': all_week,
                'timetable_day': timetable_day,
                'day_look': day_look
            },
        )

    def post(self, request):

        data = json.loads(request.body.decode())
        employee_id = int(data['employee_id'])
        patient_id = int(data['patient_id'])
        reservation_id = int(data['reservation_id'])
        hour = int(data['hour'])
        date = data['date']
        employee = MyUser.objects.get(id=employee_id)
        patient = MyUser.objects.get(id=patient_id)
        reservation = Reservation.objects.get(id=reservation_id)
        timetable, created = Timetable.objects.update_or_create(
            patient=patient, day_timetable=date,
            defaults={
                'patient': patient,
                'employee': employee,
                'day_timetable': date,
                'hour_timetable': hour,
                'reservation': reservation
            }
        )

        return HttpResponse(timetable.id)

    def delete(self, request):

        data = json.loads(request.body.decode())
        timetable_id = data['timetable_id']
        timetable = Timetable.objects.get(id=timetable_id)
        timetable.delete()

        return HttpResponse('OK')


class TimetableUserView(LoginRequiredMixin, View):

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)

        week_look = request.GET.get('week_look')
        if week_look == '0':
            week_look = set_day_look()
        week_look_data = change_day_to_data(week_look)
        all_week = generate_week_user(week_look_data)
        timetable_week = [[hour[1]] for hour in HOUR_CHOICES]
        for i in range(3):
            for j in range(5):
                item = None
                if my_user.status == 3:
                    timetable = Timetable.objects.filter(patient=my_user, day_timetable=all_week[1][j],
                                                         hour_timetable=i+1).first()
                    if timetable:
                        item = timetable.employee
                elif my_user.status == 2:
                    timetable = Timetable.objects.filter(employee=my_user, day_timetable=all_week[1][j],
                                                         hour_timetable=i + 1).first()
                    if timetable:
                        item = timetable.patient
                timetable_week[i].append(item)

        return render(
            request,
            'timetable_user.html',
            context={
                'my_user': my_user,
                'all_week': all_week,
                'timetable_week': timetable_week,
            }
        )


class ReservationUserView(LoginRequiredMixin, View):

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        today = datetime.date.today()
        reservations = Reservation.objects.filter(patient=my_user, end_reservation__gte=today)\
            .order_by('start_reservation')
        for i, reservation in enumerate(reservations):
            reservation.counter = i + 1

        return render(
            request,
            'reservation_user.html',
            context={
                'my_user': my_user,
                'reservations': reservations,
            }
        )
