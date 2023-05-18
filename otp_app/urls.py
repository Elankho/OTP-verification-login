from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate-otp/', views.generate_otp, name='generate_otp'),
    path('login/', views.login, name='login'),
]
