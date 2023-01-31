"""main URL Configuration..."""
from django.contrib import admin
from django.urls import path

from authentication import views

urlpatterns = [
    path('account/', views.RegisterView.as_view(), name='account'),
    path('base_page/', views.login_user, name='base_page'),
    path('logout_user/', views.logout_user, name='logout_user'),

]
