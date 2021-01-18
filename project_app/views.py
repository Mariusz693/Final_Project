from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView, DeleteView, View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime
from .models import MyUser, Room, Reservation
from .forms import MyUserLoginForm, MyUserCreateForm, MyUserUpdateForm, MyUserPasswordForm
from .function import generate_list, generate_month, change_date, change_date2


class IndexView(View):

    def get(self, request):

        return render(
            request,
            'index.html',
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


class PatientListView(PermissionRequiredMixin, View):

    permission_required = 'project_app.view_myuser'

    def get_login_url(self):
        return 'login'

    def get(self, request):
        if request.user.status != 1:
            return redirect('index')
        my_user_list = MyUser.objects.filter(status=3)
        option_sorted = request.GET.get('sorted')
        option_search = request.GET.get('search')
        if option_sorted == '1':
            today_is = datetime.date.today()
            reservation = Reservation.objects.filter(
                start_reservation__lte=today_is,
                end_reservation__gte=today_is
            )
            my_user_list = [item.patient for item in reservation]
        if option_search:
            if len(option_search) > 2:
                my_user_list = MyUser.objects.filter(status=3, last_name__icontains=option_search)

        message = True

        return render(
            request,
            'my_user_list.html',
            context={'my_user_list': my_user_list, 'message': message}
        )


class EmployeeListView(PermissionRequiredMixin, View):

    permission_required = 'project_app.view_myuser'

    def get_login_url(self):
        return 'login'

    def get(self, request):

        if request.user.status != 1:
            return redirect('index')

        my_user_list = MyUser.objects.filter(status=2)

        return render(
            request,
            'my_user_list.html',
            context={'my_user_list': my_user_list}
        )


class MyUserCreateView(PermissionRequiredMixin, View):

    permission_required = 'project_app.add_myuser'

    def get_login_url(self):
        return 'login'

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
            new_patient.set_permissions()

            if status == 2:
                return redirect('employee-list')
            else:
                return redirect('patient-list')

        return render(
            self.request,
            'my_user_add.html',
            context={'form': form, 'message': 'Błąd danych'}
        )


class MyUserDeleteView(PermissionRequiredMixin, DeleteView):

    permission_required = 'project_app.delete_myuser'
    model = MyUser
    template_name = 'my_user_delete.html'

    def get_login_url(self):
        return 'login'

    def delete(self, request, *args, **kwargs):
        my_user = self.get_object()

        if my_user.status == 2:
            success_url = '/employee_list/'
        else:
            success_url = '/patient_list/'

        my_user.user_permissions.clear()
        my_user.delete()

        return HttpResponseRedirect(success_url)


class MyUserUpdateView(PermissionRequiredMixin, View):

    permission_required = 'project_app.change_myuser'

    def get_login_url(self):
        return 'login'

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)
        form = MyUserUpdateForm(initial={
            'nick': my_user.username,
            'first_name': my_user.first_name,
            'last_name': my_user.last_name,
            'email': my_user.email,
            'tel_number': my_user.tel_number,
        })

        return render(
            request,
            'my_user_edit.html',
            context={'form': form, 'my_user': my_user}
        )

    def post(self, request, id_my_user):

        my_user = MyUser.objects.get(id=id_my_user)
        status = my_user.status
        form = MyUserUpdateForm(request.POST)

        if form.is_valid():
            my_user.username = form.cleaned_data['nick']
            my_user.first_name = form.cleaned_data['first_name']
            my_user.last_name = form.cleaned_data['last_name']
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


class MyUserDetailsView(PermissionRequiredMixin, View):

    permission_required = 'project_app.view_myuser'

    def get_login_url(self):
        return 'login'

    def get(self, request, id_my_user):

        if request.user.status != 1 and request.user.id != id_my_user:
            return redirect('index')

        my_user = MyUser.objects.get(id=id_my_user)

        return render(
            request,
            'my_user_details.html',
            context={'my_user': my_user}
        )


class MyUserPasswordView(PermissionRequiredMixin, View):

    permission_required = 'project_app.change_myuser'

    def get_login_url(self):
        return 'login'

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


class ReservationView(PermissionRequiredMixin, View):

    permission_required = 'project_app.view_reservation'

    def get_login_url(self):
        return 'login'

    def get(self, request):
        my_list = generate_list()
        month_look = request.GET.get('month_look')
        button = request.GET.get('button')
        if month_look:
            month_look = int(month_look)
        else:
            month_look = my_list[0][0]
        button_active = [True, True]
        if button == 'prev_month':
            month_look -= 1
        if button == 'next_month':
            month_look += 1

        if month_look == 1:
            button_active[0] = False
        if month_look == 24:
            button_active[1] = False

        my_month = my_list[month_look-1]
        max_date = my_list[-1][5]
        min_date = my_list[0][5]
        print(max_date, min_date)
        month_list = generate_month(my_month, my_list)
        week_list = month_list[0]
        day_list = month_list[1]
        day_name = month_list[2]
        day_month_start = day_list[0]
        day_month_end = day_list[-1]
        rooms = Room.objects.all()
        for room in rooms:
            reservation_all = room.reservation_set.filter(
                start_reservation__lte=day_month_end,
                end_reservation__gte=day_month_start
            ).order_by('start_reservation')
            result_table = []
            counter = 0
            for reservation in reservation_all:
                start_reservation = reservation.start_reservation
                end_reservation = reservation.end_reservation
                if (start_reservation - day_month_start).days <= 0:
                    start_reservation = day_month_start
                else:
                    free_time = day_list.index(start_reservation) - counter
                    prev_reservation = room.reservation_set.filter(
                        end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                    next_reservation = room.reservation_set.filter(
                        start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                    result_table.append([
                        False,
                        free_time,
                        prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date,
                        next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date,
                    ])
                    counter += free_time
                if (end_reservation - day_month_end).days > 0:
                    end_reservation = day_month_end
                during_reservation = (end_reservation - start_reservation).days + 1
                result_table.append([True, during_reservation, reservation])
                counter += during_reservation
            counter = 0
            for item in result_table:
                counter += item[1]
            free_time = (len(week_list) * 7) - counter
            if free_time:
                prev_reservation = room.reservation_set.filter(
                    end_reservation__lte=day_list[counter]).order_by('-end_reservation').first()
                next_reservation = room.reservation_set.filter(
                    start_reservation__gte=day_list[counter]).order_by('start_reservation').first()
                result_table.append([
                    False,
                    free_time,
                    prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date,
                    next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date,
                ])

            room.reserve = result_table

        return render(
                request,
            'reservation.html',
                context={
                    'my_list': my_list,
                    'my_month': my_month,
                    'button_active': button_active,
                    'week_list': week_list,
                    'day_name': day_name,
                    'rooms': rooms,
                }
            )


class ReservationAddView(View):

    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        room_id = request.GET.get('room')
        start = change_date(start)
        end = change_date(end)
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

            return redirect('reservation')


class ReservationEditView(View):

    def get(self, request, id_reservation):
        reservation = Reservation.objects.get(id=id_reservation)
        room = reservation.room
        prev_reservation = room.reservation_set.filter(
            end_reservation__lte=reservation.start_reservation).order_by('-end_reservation').first()
        next_reservation = room.reservation_set.filter(
            start_reservation__gte=reservation.end_reservation).order_by('start_reservation').first()
        my_list = generate_list()
        max_date = my_list[-1][5]
        min_date = my_list[0][5]
        start = prev_reservation.end_reservation + datetime.timedelta(days=1) if prev_reservation else min_date
        start = change_date2(start)
        end = next_reservation.start_reservation - datetime.timedelta(days=1) if next_reservation else max_date
        end = change_date2(end)
        reservation.start_reservation_change = change_date2(reservation.start_reservation)
        reservation.end_reservation_change = change_date2(reservation.end_reservation)
        patient_list = MyUser.objects.filter(status=3)

        return render(
            request,
            'reservation_form.html',
            context={'room': room, 'reservation': reservation, 'start': start, 'end': end, 'patient_list': patient_list}
        )

    def post(self, request, id_reservation):
        reservation = Reservation.objects.get(id=id_reservation)
        button = request.POST.get('button')
        if button == 'Zapisz':
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
                    reservation.start_reservation_change = change_date2(reservation.start_reservation)
                    reservation.end_reservation_change = change_date2(reservation.end_reservation)

                    return render(
                        self.request,
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

        elif button == 'Usuń':
            reservation.delete()

        return redirect('reservation')


