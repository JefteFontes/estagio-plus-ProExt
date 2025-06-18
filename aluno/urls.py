from django.urls import path
from .views import cadastro_aluno, estagios_aluno

urlpatterns = [
    path('cadastro/', cadastro_aluno, name='cadastro_aluno'),
    path('dashboard/estagios-aluno/', estagios_aluno, name='estagios_aluno'),
]
