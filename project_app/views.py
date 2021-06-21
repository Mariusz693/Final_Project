import datetime
import json

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, FormView, DeleteView, CreateView, UpdateView, DetailView, ListView
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

from .models import User, Room, Reservation, Timetable, UserUniqueToken
from .forms import UserLoginForm, UserPasswordUpdateForm, UserPasswordSetForm, UserPasswordResetForm, ReservationAddForm, \
     ReservationUpdateForm, TimetableAddForm, TimetableUpdateForm, ContactForm
from .utils import generate_list, generate_month, generate_week_timetable, change_day_to_date, set_day_look


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
    	
        return self.request.GET.get('next') or reverse_lazy('index')

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


class PatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Return a list of all patient sorted by last name, patient currently in the middle, or last name search results
    Only for user with status admin
    """
    template_name = 'user_list.html'
    paginate_by = 8

    def test_func(self):

        return self.request.user.status == 1

    def get_queryset(self):
        
        search = self.request.GET.get('search')
        search = search if search else ''
        
        if search == 'actually_patient':
            today = set_day_look()
            reservations = Reservation.objects.filter(
                start_date__lte=today,
                end_date__gte=today
            ).order_by('room')
            object_list = []
            
            for reservation in reservations:
                reservation.patient.counter = reservation.room
                object_list.append(reservation.patient)
        
        else:
            object_list = User.objects.filter(status=3, last_name__icontains=search).order_by('last_name')
        
            for i, patient in enumerate(object_list):
                patient.counter = i + 1

        return object_list

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        context['message'] = self.request.GET.get('search')
        
        return context


class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Return a list of all employee sorted by last name
    Only for user with status admin
    """
    template_name = 'user_list.html'
    paginate_by = 8

    def test_func(self):
        
        return self.request.user.status == 1

    def get_queryset(self):
        
        object_list = User.objects.filter(status=2).order_by('last_name')
        
        for i, employee in enumerate(object_list):
            employee.counter = i + 1

        return object_list

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        context['message_employee'] = True
        
        return context


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
    
    def get_success_url(self, user):
       
        if user.status == 2:
            
            return reverse_lazy('employee-list')
    
        if user.status == 3:    
            
            return reverse_lazy('patient-list')
        
        return reverse_lazy('index')
    
    def get_initial(self):

        initial = super().get_initial()
        status = self.request.GET.get('status')
        
        if status:
            initial['status'] = 2 if status == 'employee' else 3 
        
        return initial
    
    def create_user(self, valid_data, commit=False):
        
        return User.objects.create_user(
            email=valid_data['email'],
            first_name=valid_data['first_name'],
            last_name=valid_data['last_name'],
            phone=valid_data['phone'],
            status=int(valid_data['status']),
            is_active=False
        )

    def send_mail(self, user):

        new_token = UserUniqueToken.objects.create(user=user)
        send_mail(
            subject='Rejestracja konta',
            message=f'''Twoje konto zostało utworzone w naszym serwisie, twój link do aktywacji konta:
                {self.request.get_host()}{reverse_lazy('user-password-set')}?token={new_token.token}''',
            from_email=self.request.user.email,
            recipient_list=[user.email],
        )

    def form_valid(self, form):
        
        user = self.create_user(form.cleaned_data)
        
        self.send_mail(user)

        return HttpResponseRedirect(self.get_success_url(user))


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    Return the delete person form view, patient or employee
    Only for user with status admin
    """
    model = User
    template_name = 'user_delete.html'
   
    def get_object(self):

        if self.request.user.status == 1 and self.request.GET.get('pk'):
        
            return get_object_or_404(User, id=self.request.GET.get('pk'))
        
        return self.request.user

    def get_success_url(self):
    
        return self.request.GET.get('next') or reverse_lazy('index')
    
    def delete(self, request, *args, **kwargs):
        
        try:
        
            return super().delete(request, *args, **kwargs)
        
        except ValidationError as e:
        
            self.object = self.get_object()
            context = self.get_context_data(
                object=self.object,
                errors=e
            )
        
            return self.render_to_response(context)
     

class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Return the edit person form view of patient or employee
    All user
    """
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone']
    template_name = 'user_update.html'
    success_url = reverse_lazy('user-details')
    
    def get_object(self):
       
        return self.request.user

    
class UserDetailsView(LoginRequiredMixin, DetailView):
    """
    Return the view of details patient, employee or admin
    All user
    """
    model = User
    template_name = 'user_details.html'
    
    def get_object(self):

        return self.request.user


class UserPasswordUpdateView(LoginRequiredMixin, FormView):
    """
    Return the change password form view of patient, employee or admin
    All user
    """    
    form_class = UserPasswordUpdateForm
    template_name = 'user_password_update.html'
    success_url = reverse_lazy('user-details')

    def get_form_kwargs(self, *args, **kwargs):
        
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['email'] = self.request.user.email
        
        return kwargs

    def form_valid(self, form):
    
        user = self.request.user
        password = form.cleaned_data['password_new']
        user.set_password(password)
        user.save()
        
        return super().form_valid(form)


class UserPasswordSetView(FormView):
    """
    Return the set password form view of patient, employee or admin
    All user
    """    
    form_class = UserPasswordSetForm
    template_name = 'user_password_set.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):

        token = self.request.GET.get('token')    
        user_unique_token = get_object_or_404(UserUniqueToken, token=token)
        user = user_unique_token.user
        password = form.cleaned_data['password_new']
        user.is_active = True
        user.set_password(password)
        user.save()
        user_unique_token.delete()

        return super().form_valid(form)



class UserPasswordResetView(FormView):

    form_class = UserPasswordResetForm
    template_name = 'user_password_reset.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):

        url = f"{self.request.get_host()}{reverse_lazy('user-password-set')}"
        form.send_mail(url)

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
        if not month_look:
            today = datetime.date.today()
            month_look = str(today)[:-3]
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
        one_day = datetime.timedelta(days=1)
        rooms = Room.objects.all()
        for room in rooms:
            reservation_all = room.reservation_set.filter(
                start_date__lte=month_day_end,
                end_date__gte=month_day_start
            ).order_by('start_date')
            result_table = []
            counter = 0
            for reservation in reservation_all:
                start_date = reservation.start_date
                end_date = reservation.end_date
                if (start_date - month_day_start).days <= 0:
                    start_date = month_day_start
                else:
                    free_time = day_list.index(start_date) - counter
                    if free_time:
                        prev_reservation = room.reservation_set.filter(
                            end_date__lte=day_list[counter]
                        ).order_by('-end_date').first()
                        next_reservation = room.reservation_set.filter(
                            start_date__gte=day_list[counter]
                        ).order_by('start_date').first()
                        result_table.append([
                            False,
                            free_time,
                            prev_reservation.end_date + one_day if prev_reservation else None,
                            next_reservation.start_date - one_day if next_reservation else None
                        ])
                        counter += free_time
                if (end_date - month_day_end).days > 0:
                    end_date = month_day_end
                during_reservation = (end_date - start_date).days + 1
                result_table.append([
                    True, 
                    during_reservation, 
                    reservation,
                    [
                        True if reservation.start_date < month_day_start else False,
                        True if reservation.end_date > month_day_end else False
                    ]
                ])
                counter += during_reservation
            counter = 0
            for item in result_table:
                counter += item[1]
            free_time = selected_month_len - counter
            if free_time:
                prev_reservation = room.reservation_set.filter(end_date__lte=day_list[counter]).order_by('-end_date').first()
                next_reservation = room.reservation_set.filter(start_date__gte=day_list[counter]).order_by('start_date').first()
                result_table.append([
                    False,
                    free_time,
                    prev_reservation.end_date + one_day if prev_reservation else None,
                    next_reservation.start_date - one_day if next_reservation else None
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


class ReservationAddView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Return the add reservation view
    Only for user with status admin
    """
    model = Reservation
    template_name = 'reservation_add.html'
    form_class = ReservationAddForm
    
    def test_func(self):
        
        return self.request.user.status == 1

    def get_success_url(self):

        return self.request.GET.get('next') or reverse_lazy('reservation')
    
    def get_form_kwargs(self, *args, **kwargs):
        
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['room'] = self.request.GET.get('room')
        kwargs['date'] = self.request.GET.get('date')
        
        return kwargs


class ReservationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Return the edit reservation view
    Only for user with status admin
    """
    model = Reservation
    template_name = 'reservation_update.html'
    form_class = ReservationUpdateForm
    
    def test_func(self):
        
        return self.request.user.status == 1

    def get_success_url(self):

        return self.request.GET.get('next') or reverse_lazy('reservation')
    
    def form_valid(self, form):
        
        reservation = form.save()
        
        timetables = reservation.timetable_set.filter(
            Q(day_timetable__lt=reservation.start_date) | Q(day_timetable__gt=reservation.end_date)
        )
        if timetables:
            timetables.delete()

        return super().form_valid(form)


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

        return self.request.GET.get('next') or reverse_lazy('reservation')


@method_decorator(csrf_exempt, name='dispatch')
class TimetableView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Return the view where user may add or delete timetable for patient currently in the middle
    Only for user with status admin
    """
    def test_func(self):
        
        return self.request.user.status == 1

    def get(self, request):

        month_list = generate_list()
        day_look = request.GET.get('day_look')
        day_look = set_day_look(day_look)
        all_week = generate_week_timetable(day_look)
        employee_list = User.objects.filter(status=2, is_active=True)
        reservations = Reservation.objects.filter(start_date__lte=day_look, end_date__gte=day_look)
        patient_list = []
        for reservation in reservations:
            patient = reservation.patient
            patient.reservation_id = reservation.id
            patient_list.append(patient)
        timetables = Timetable.objects.filter(day_timetable=day_look)
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
                'day_look': day_look,
                'month_list': month_list
            },
        )

    def post(self, request):

        data = json.loads(request.body.decode())
        form = TimetableAddForm(data)
        
        if form.is_valid():
            timetable = form.save()

            return JsonResponse({'instance': timetable.id}, status=200)

    def put(self, request):
        
        data = json.loads(request.body.decode())
        form = TimetableUpdateForm(data)
        form.instance = get_object_or_404(Timetable, id=int(data['timetable']))

        if form.is_valid():
            form.save()
        
            return JsonResponse({}, status=200)

    def delete(self, request):
        
        data = json.loads(request.body.decode())
        timetable = get_object_or_404(Timetable, id=int(data['timetable']))
        timetable.delete()
    
        return JsonResponse({}, status=200)


class UserTimetableView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Return view of the timetable for current user (patient or employee)
    All user
    """
    def test_func(self):
        
        return self.request.user.status == 1 or self.kwargs['pk'] == self.request.user.id
    
    def get(self, request, pk):

        month_list = generate_list()
        user = get_object_or_404(User, id=pk)
        week_look = request.GET.get('week_look')
        week_look = set_day_look(week_look)
        all_week = generate_week_timetable(week_look)
        timetable_week = [[hour[1]] for hour in Timetable.HOUR_CHOICES]
        
        for i in range(3):
        
            for j in range(5):
                item = None
        
                if user.status == 3:
                    timetable = Timetable.objects.filter(patient=user, day_timetable=all_week[0][j],
                                                         hour_timetable=i+1).first()
                    if timetable:
                        item = timetable.employee
        
                elif user.status == 2:
                    timetable = Timetable.objects.filter(employee=user, day_timetable=all_week[0][j],
                                                         hour_timetable=i+1).first()
                    if timetable:
                        item = timetable.patient
        
                timetable_week[i].append(item)
        
        return render(
            request,
            'user_timetable.html',
            context={
                'user': user,
                'all_week': all_week,
                'timetable_week': timetable_week,
                'month_list': month_list
            }
        )


class UserReservationView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Return view of the reservation for current patient
    All user
    """
    template_name = 'user_reservation.html'
    paginate_by = 8

    def test_func(self):

        return self.request.user.status == 1 or self.kwargs['pk'] == self.request.user.id
    
    def get_queryset(self, *args, **kwargs):
        
        self.patient = get_object_or_404(User, id=self.kwargs['pk']) 
        self.search = self.request.GET.get('search') if self.request.GET.get('search') else 'next'
        self.today = datetime.date.today()
        
        if self.search == 'prev':
            object_list = Reservation.objects.filter(patient=self.patient, end_date__lte=self.today).order_by('-end_date')
        else:
            object_list = Reservation.objects.filter(patient=self.patient, start_date__gte=self.today).order_by('start_date')
        
        return object_list

    def get_context_data(self, *args, **kwargs):
        
        context = super().get_context_data(*args, **kwargs)
        
        context['reservation'] = Reservation.objects.filter(
            patient=self.patient, 
            start_date__lte=self.today, 
            end_date__gte=self.today
            ).first()
        context['patient'] = self.patient
        context['search'] = self.search

        return context


class ContactView(FormView):

    form_class = ContactForm
    success_url = reverse_lazy('index')
    template_name = 'contact_form.html'

    def form_valid(self, form):

        admins = User.objects.filter(status=1).values_list('email')
        emails_to_send = [admin[0] for admin in admins]
        send_mail(
            subject=form.cleaned_data['subject'],
            message=f'''
            Imię: {form.cleaned_data['first_name']},
            Nazwisko: {form.cleaned_data['last_name']},
            Telefon: {form.cleaned_data['phone']},
            Wiadomość: {form.cleaned_data['message']},
            ''',
            from_email=form.cleaned_data['email'],
            recipient_list=emails_to_send,
        )
        
        return super().form_valid(form)
