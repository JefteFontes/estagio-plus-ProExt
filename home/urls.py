from django.urls import path
from . import views
from dashboard.views.utils import validate_cnpj, validate_cpf, buscar_cep

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro-instituicao', views.cadastrar_instituicao, name='cadastro_instituicao'),
    path('validate_cnpj/', validate_cnpj, name='validate_cnpj'),
    path('validate_cpf/', validate_cpf, name='validate_cpf'),
    path('buscar_cep/', buscar_cep, name='buscar_cep'),
]
