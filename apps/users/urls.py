# apps/users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import logout_view

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', logout_view, name='logout'),
]