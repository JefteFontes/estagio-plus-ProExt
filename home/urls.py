from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro-instituicao', views.cadastrar_instituicao, name='cadastro_instituicao'),
]
