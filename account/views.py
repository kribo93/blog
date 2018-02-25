from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from account.forms import UserAdminCreationForm, AuthForm
from django.contrib.messages.views import SuccessMessageMixin
from account.models import Post, Profile, User
from django.db.models import Q
from django.contrib import messages
from django.http import Http404
# Create your views here.

#class HomePageView(TemplateView):
#    template_name = 'account/home.html'

#    @method_decorator(login_required(login_url='/account/login/'))
#    def dispatch(self, *args, **kwargs):
#        return super(HomePageView, self).dispatch(*args, **kwargs)



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



class PostListView(ListView):
    model = Post
    template_name = 'account/post_list.html'
    paginate_by = 7

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) |
                                          Q(body__icontains=query)
                                          ).distinct()
            return queryset
        else:
            return Post.published.all()


class PostDetailView(DetailView):
    model = Post
    template_name = 'account/detail.html'

class ProfileView(DetailView):
    model = Profile
    template_name = 'account/profile_page.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['profile'] = Profile.objects.filter(user=self.kwargs['pk'])
        context['author'] = Post.objects.filter(author=self.kwargs['pk'])
        print(context['profile'])
        return context

class ProfileList(ListView):
    model = Profile
    template_name = 'account/profile_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(ProfileList, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = Profile.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(user__first_name__icontains=query) |
                                       Q(user__last_name__icontains=query) |
                                       Q(nickname__icontains=query) |
                                       Q(user__email__icontains=query)
                                          ).distinct()
            return queryset
        else:
            return Profile.objects.all()

class CreatePostView(SuccessMessageMixin,LoginRequiredMixin, CreateView):
    login_url = '/account/login/'

    template_name = 'account/post_create.html'
    success_url = '/'
    model = Post
    success_message = "Post was created successfully"
    fields = ('image','title', 'body', 'status', )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = form.instance.title
        form.instance.image = form.cleaned_data['image']
        form.save()
        return super(CreatePostView, self).form_valid(form)













"""Пробы


class ProfileView(DetailView):
    model = Profile
    template_name = 'account/profile_page.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated():

            context = super(ProfileView, self).get_context_data(**kwargs)
            context['profile'] = Profile.objects.filter(user=self.kwargs['pk'])
            context['author'] = Post.objects.filter(author=self.kwargs['pk'])
            return context
        else:
            context = super(ProfileView, self).get_context_data(**kwargs)
            context['profile'] = Profile.objects.filter(user=self.request.user)
            context['author'] = Post.objects.filter(author=self.request.user)
        return context

class MyProfileView(DetailView):
    model = Profile
    template_name = 'account/profile_page.html'
    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated():
            messages.add_message(self.request, messages.INFO, 'You are not logged-in!')
            context = super(MyProfileView, self).get_context_data(**kwargs)
            context['profile'] = Profile.objects.all()
            return context
        else:
            context = super(MyProfileView, self).get_context_data(**kwargs)
            context['profile'] = Profile.objects.filter(user=self.request.user)
            context['author'] = Post.objects.filter(author=self.request.user)

            print(context['profile'])

        return context



def get_object(self, queryset=None):
    try:
        userk = User.objects.filter(id=self.kwargs['pk'])
        userr = Profile.objects.filter(user__id=self.kwargs['pk'])
        my_object = Profile.objects.get(user__id=1)

        print(userr)
        print(userk)
        return self.model.objects.filter(user=userk)

    except self.model.DoesNotExist:
        raise Http404("No Model matches the given query.")



"""