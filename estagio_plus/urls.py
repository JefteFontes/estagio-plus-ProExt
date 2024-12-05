from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("allauth.urls")),
    path('accounts/profile/', include('dashboard.urls')),
    path('home/', include('home.urls')),
]
