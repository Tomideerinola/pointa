from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('user/signup/', views.user_signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path("user/login/", views.user_login, name="user_login"),
    path("organizer/signup/", views.organizer_signup, name="organizer_signup"),
    path('organizer/login/', views.organizer_login, name='organizer_login'),
    path('organizer/dashboard/', views.org_dashboard, name='org_dashboard'),
    path("organizer/logout/", views.organizer_logout, name="organizer_logout"),
    path('create/event/', views.create_event, name="create_event"),
    path('event/<int:event_id>/', views.event_detail, name="event_detail"),
    path('event/list/', views.events_list, name='events_list')

]