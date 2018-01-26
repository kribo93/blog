from django.conf.urls import url
from django.contrib import admin
from account.views import HomePageView, LoginView, LogoutView, SignUpView

urlpatterns = [
    url(r'^home/$', HomePageView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='my_logout'),
    url(r'^signup/$', SignUpView.as_view(), name='sign_up'),

]