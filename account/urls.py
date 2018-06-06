from django.conf.urls import url, include
from django.contrib import admin
from account.views import LoginView, LogoutView, SignUpView, PostListView,PostDetailView, PostCreateView,ProfileView, \
     ProfileListView, RegisterView, PostUpdateView,PostDeleteView, CommentAdd, ProfileUpdateView, AccountUpdateView, \
     TagIndexView
from . import views

urlpatterns = [

    url(r'^login/$', LoginView.as_view(),  name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='my_logout'),
    url(r'^signup/$', RegisterView.as_view(), name='sign_up'),
    #url(r'^post_list/$', PostListView.as_view(), name='post_list'),
    url(r'^post_create/$', PostCreateView.as_view(), name='post_create'),
    url(r'^post/(?P<pk>\d+)/update/$', PostUpdateView.as_view(), name='post_update'),
    url(r'^post/(?P<pk>\d+)/delete/$', PostDeleteView.as_view(), name='post_delete'),
    url(r'^tag/(?P<slug>[-\w]+)/$', TagIndexView.as_view(), name='tagged'),
    url(r'^blog/(?P<pk>\d+)/$', PostDetailView.as_view(), name='post_detail'),
    url(r'^profile/(?P<pk>\d+)/details/$', ProfileView.as_view(), name='profile'),
    url(r'^profile/$', ProfileListView.as_view(), name='profile_list'),
    url(r'^profile/(?P<pk>\d+)/settings/$', ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^account_update/(?P<pk>\d+)/$', AccountUpdateView.as_view(), name='account_update'),
    url(r'^comment/add/$', CommentAdd.as_view(), name='comment_add'),
    url(r'^like/$', views.post_like, name='like'),
    url(r'^select2/', include('django_select2.urls')),
]