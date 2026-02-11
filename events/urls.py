from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('user/signup/', views.user_signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
     path("user/login/", views.user_login, name="user_login"),
     path("organizer/signup/", views.organizer_signup, name="organizer_signup"),
     path('organizer/dashboard/', views.org_dashboard, name='org_dashboard'),
]