from django.urls import path
from django.contrib.auth import views as av
from core import views as v
urlpatterns=[path('',v.dashboard,name='dash'),path('login/',av.LoginView.as_view(template_name='core/login.html'),name='login'),
path('logout/',av.LogoutView.as_view(),name='logout'),path('register/',v.register,name='register'),
path('log/<str:cat>/',v.log,name='log'),path('leaderboard/',v.leaderboard,name='lb'),path('company/',v.company,name='company')]
