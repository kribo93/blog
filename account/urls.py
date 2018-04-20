from django.conf.urls import url
from django.contrib import admin
from account.views import LoginView, LogoutView, SignUpView, PostListView,PostDetailView, PostCreateView,ProfileView, ProfileList, RegisterView, PostUpdateView,PostDeleteView, CommentAdd

urlpatterns = [

    url(r'^login/$', LoginView.as_view(),  name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='my_logout'),
    url(r'^signup/$', RegisterView.as_view(), name='sign_up'),
    #url(r'^post_list/$', PostListView.as_view(), name='post_list'),
    url(r'^post_create/$', PostCreateView.as_view(), name='post_create'),
    url(r'^post/(?P<pk>\d+)/update/$', PostUpdateView.as_view(), name='post_update'),
    url(r'^post/(?P<pk>\d+)/delete/$', PostDeleteView.as_view(), name='post_delete'),
    url(r'^blog/(?P<pk>\d+)/$', PostDetailView.as_view(), name='post_detail'),
    url(r'^profile/(?P<pk>\d+)/details/$', ProfileView.as_view(), name='profile'),
    url(r'^profile/$', ProfileList.as_view(), name='profile_list'),
    url(r'^comment/add/$', CommentAdd.as_view(), name='comment_add'),
]