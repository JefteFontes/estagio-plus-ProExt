from django.urls import path
from base.views import profile_redirect

app_name = "base"

urlpatterns = [
    path('', profile_redirect, name='profile_redirect'),
]
