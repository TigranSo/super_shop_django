from django.contrib import admin
from django.urls import path

from users import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_user, name='logout'),
]