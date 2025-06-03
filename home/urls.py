from django.urls import path, re_path
from . import views
from dashboard.views.utils import validate_cnpj, validate_cpf, buscar_cep
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('pre-cadastro', views.pre_cadastro, name='pre_cadastro'),
    path('cadastro-instituicao', views.cadastrar_instituicao, name='cadastro_instituicao'),
    path('cadastro-aluno', views.cadastro_aluno, name='cadastro_aluno'),
    path('ajax/load-cursos/', views.load_cursos, name='load_cursos'),
    path('validate_cnpj/', validate_cnpj, name='validate_cnpj'),
    path('validate_cpf/', validate_cpf, name='validate_cpf'),
    path('buscar_cep/', buscar_cep, name='buscar_cep'),
    path('<str:pdf_nome>/', views.visualizar_termo, name='visualizar_termo'),
    re_path(r'(?P<pdf_nome>.+)/$', views.visualizar_termo, name='visualizar_termo'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
