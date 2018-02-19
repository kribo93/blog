from django.conf.urls import url
from django.contrib import admin
from account.views import LoginView, LogoutView, SignUpView, PostListView,PostDetailView, CreatePostView

urlpatterns = [

    url(r'^login/$', LoginView.as_view(),  name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='my_logout'),
    url(r'^signup/$', SignUpView.as_view(), name='sign_up'),
    #url(r'^post_list/$', PostListView.as_view(), name='post_list'),
    url(r'^post_create/$', CreatePostView.as_view(), name='post_create'),

    url(r'^(?P<pk>\d+)/$', PostDetailView.as_view(), name='post_detail'),
]