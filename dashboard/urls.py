from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_instituicao, name='dashboard_instituicao'),
]
