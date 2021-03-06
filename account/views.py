from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView, View
from django.contrib.auth.decorators import login_required
from account.forms import UserAdminCreationForm, AuthForm
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'account/home.html'

    @method_decorator(login_required(login_url='/account/login/'))
    def dispatch(self, *args, **kwargs):
        return super(HomePageView, self).dispatch(*args, **kwargs)


class LoginView(FormView):
    """
       Provides the ability to login as a user with a username and password
    """
    template_name = 'account/login.html'
    success_url = '/'
    form_class = AuthForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)

    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/account/login/'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class SignUpView(SuccessMessageMixin, FormView):
    template_name = 'account/signup.html'
    success_url = '/'
    form_class = UserAdminCreationForm
    success_message = "Account was created successfully"

    def form_valid(self, form):
        form.save()
        # get the username and password
        email = self.request.POST['email']
        password = self.request.POST['password1']
        # authenticate user then login
        new_user = authenticate(email=email, password=password)
        auth_login(self.request, new_user)
        return super(SignUpView, self).form_valid(form)


