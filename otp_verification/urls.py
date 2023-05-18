from django.urls import path, include
from otp_app.views import home
from django.contrib import admin

urlpatterns = [
    path('', home, name='home'),
    path('api/', include('otp_app.urls')),
    path('admin/', admin.site.urls),
    # Other URL patterns for your project
]
