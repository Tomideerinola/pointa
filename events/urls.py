from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('user/signup/', views.user_signup, name='signup'),
    path('org/signup/', views.org_signup, name='org_signup'),
    path('login/', views.login, name='loginy'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
     path("user/login/", views.user_login, name="user_login"),
]