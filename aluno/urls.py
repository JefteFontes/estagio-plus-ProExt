from django.urls import path
from .views import cadastro_aluno

urlpatterns = [
    path('cadastro/', cadastro_aluno, name='cadastro_aluno'),
]
