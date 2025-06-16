from django.urls import path
from .views import cadastro_aluno, dashboard_aluno

urlpatterns = [
    path('cadastro/', cadastro_aluno, name='cadastro_aluno'),
    path('dashboard/', dashboard_aluno, name='dashboard_aluno'),
]
