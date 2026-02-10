from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('user/signup/', views.user_signup, name='signup'),
    path('org/signup/', views.org_signup, name='org_signup'),
    path('login/', views.login, name='login'),
]