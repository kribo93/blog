from django.utils.http import is_safe_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView, ListView, DetailView, UpdateView,DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from account.forms import UserAdminCreationForm, AuthForm, UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from account.models import Post, Profile, User, Comment
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from .forms import CommentForm
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
        profile = Profile.objects.create(nickname=self.request.user.nickname, user=self.request.user)
        # get the username and password
        email = self.request.POST['email']
        password = self.request.POST['password1']
        # authenticate user then login
        new_user = authenticate(email=email, password=password)
        auth_login(self.request, new_user)
        return super(SignUpView, self).form_valid(form)

class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'account/signup.html'
    success_url = '/'
    form_class = UserCreationForm
    success_message = "Account was created successfully"

    def form_valid(self, form):
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
        )
        profile = Profile.objects.create(nickname=form.cleaned_data['nickname'], user=user)

        auth_login(self.request, user)
        return super(RegisterView, self).form_valid(form)


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
    template_name = 'account/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['comment_form'] = CommentForm(initial={'post':self.object, 'nickname':self.request.user.profile.pk})
        return context

class ProfileView(DetailView):
    model = Profile
    template_name = 'account/profile_page.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.kwargs['pk'])
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

class PostCreateView(SuccessMessageMixin,LoginRequiredMixin, CreateView):
    login_url = '/account/login/'

    template_name = 'account/post_create.html'
    success_url = '/'
    model = Post
    success_message = "Post was created successfully"
    fields = ('title', 'body', 'status', )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = form.instance.title
        form.save()
        return super(PostCreateView, self).form_valid(form)

class PostUpdateView(SuccessMessageMixin,LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'account/post_update.html'
    login_url = '/login/'
    success_message = "Post was updated successfully"
    success_url = reverse_lazy('account:profile')
    fields = ('title', 'body', 'status',)

    def get_success_url(self):
        return reverse_lazy('account:profile', kwargs={'pk': self.request.user.id})

class PostDeleteView(SuccessMessageMixin,LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'account/post_delete.html'
    login_url = '/login/'
    success_message = "Post was deleted successfully"

    def get_success_url(self):
        return reverse_lazy('account:profile', kwargs={'pk': self.request.user.id})

class CommentAdd(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'account/comment_add.html'



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

class UserCreateView(FormView):

    # url to redirect to after successful form submission
    success_url = '/'
    template_name = 'account/signup.html'
    success_message = "Account was created successfully"

    def get_context_data(self, *args, **kwargs):
        data = super(UserCreateView, self).get_context_data(**kwargs)
        data['userform'] = self.get_form(UserAdminCreationForm, 'user')
        data['userprofileform'] = self.get_form(UserProfileForm, 'userprofile')
        return data

    def post(self, request, *args, **kwargs):
        forms = dict((
            ('userform', self.get_form(UserAdminCreationForm, 'user')),
            ('userprofileform', self.get_form(UserProfileForm, 'userprofile')),
        ))
        if all([f.is_valid() for f in forms.values()]):
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)

    def get_form(self, form_class=None, prefix):
        if form_class is None:
            form_class = self.form_class
        return form_class(**self.get_form_kwargs(prefix))

    def get_form_kwargs(self, prefix):
        kwargs = super(UserCreateView, self).get_form_kwargs()
        kwargs.update({'prefix': prefix})
        return kwargs

    def form_valid(self, forms):
        user = forms['userform'].save()
        userprofile = forms['userprofileform'].save(commit=False)
        userprofile.user_id = user.id
        userprofile.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

"""