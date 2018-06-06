from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from .models import User, Post, Profile, Comment
from account.utils import BootstrapMixin
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponseRedirect
from django.utils import timezone
from taggit.models import Tag
from django_select2.forms import Select2MultipleWidget

class UserAdminCreationForm(BootstrapMixin, forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=False):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserCreationForm(BootstrapMixin, forms.Form):
    email = forms.EmailField(label='email address',
                              max_length=255)

    nickname = forms.CharField(label='nickname', max_length=20)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Profile "%s" is already in use.' % email)
        else:
            return email
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        filtered = Profile.objects.filter(nickname=nickname).exists()
        if filtered:
            raise forms.ValidationError('Profile "%s" is already in use.' % nickname)
        return nickname



class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class AuthForm(BootstrapMixin, AuthenticationForm):

    pass

def past_years(ago):
    this_year = timezone.now().year
    return list(range(this_year-ago-1, this_year))

class ProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)
        widgets = {
            'nickname': forms.TextInput(attrs={'size': 50, 'title': 'Enter your nickname'}),
            'date_of_birth': forms.SelectDateWidget(years=past_years(100))
        }

class CommentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('nickname', 'body', 'post')
        widgets = {'nickname': forms.HiddenInput(), 'post': forms.HiddenInput(),
                   'body': forms.Textarea(attrs={'size': 100, 'placeholder': 'Enter your comment', 'rows': 2, 'cols':  100 })}

class PostForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'tags', 'body', 'status']
        widgets = {
            'tags' : Select2MultipleWidget()
        }


class AccountUpdateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
