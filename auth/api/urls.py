from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.api_overview, name='services'),
    path('ulist/', views.userList, name='ulist'),
    path('auth-list/', views.authentication, name='auth-list'),
    path('auth-register/', views.registration, name='auth-regis'),
    path('activate/<str:uidb64>/<slug:token>',views.emailverification, name='activate'),

]

