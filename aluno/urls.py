from django.urls import path
from .views import cadastro_aluno, estagios_aluno, detalhes_estagio_aluno

urlpatterns = [
    path('cadastro/', cadastro_aluno, name='cadastro_aluno'),
    path('dashboard/estagios-aluno/', estagios_aluno, name='estagios_aluno'),
    path('dashboard/estagio/<int:pk>/', detalhes_estagio_aluno, name='detalhes_estagio_aluno'),
]
