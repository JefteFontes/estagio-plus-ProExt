from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_instituicao, name='dashboard_instituicao'),
    path('details/', views.details, name='details'),
    path('detalhes/', views.detalhes_vaga, name='detalhes_vaga'),
]
