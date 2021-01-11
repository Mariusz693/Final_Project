from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView, DeleteView, View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from .models import MyUser
from .forms import MyUserLoginForm, MyUserCreateForm, MyUserUpdateForm, MyUserPasswordForm


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
        button = request.POST.get('button')

        if my_user.status == 2:
            success_url = '/employee_list/'
        else:
            success_url = '/patient_list/'

        if button == 'Potwierdź':
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
        button = request.POST.get('button')

        if button == 'Potwierdź':
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

                if status == 2 or status == 3:
                    return redirect('my-user-details', my_user.id)

            return render(
                self.request,
                'my_user_edit.html',
                context={'form': form, 'message': 'Błąd danych'}
            )

        else:
            if request.user.status == 1:
                if status == 2:
                    return redirect('employee-list')
                if status == 3:
                    return redirect('patient-list')

            if status == 2 or status == 3:
                return redirect('my-user-details', my_user.id)


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
        form = MyUserPasswordForm(initial={
            'password': '- - -',
            'repeat_password': '-----',
        })

        return render(
            request,
            'my_user_password.html',
            context={'form': form, 'my_user': my_user}
        )

    def post(self, request, id_my_user):

        my_user = MyUser.objects.get(id=id_my_user)
        status = my_user.status
        form = MyUserPasswordForm(request.POST)
        button = request.POST.get('button')

        if button == 'Potwierdź':
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

        else:
            if request.user.status == 1:
                if status == 2:
                    return redirect('employee-list')

                return redirect('patient-list')

            return redirect('my-user-details', my_user.id)
