from django.urls import include, path
from dashboard.views.empresa import cadastrar_empresa
from dashboard.views.estagiarios import cadastrar_estagiario
from dashboard.views.pdfimport import importar_pdf
from dashboard.views.estagios import detalhes_estagio
from dashboard.views.utils import parse_sections, buscar_cep, validate_cnpj
from dashboard.views.home import home, details, dashboard_instituicao, dashboard_empresa, dashboard_estagiario, dashboard_cursos,cadastrar_cursos,deletar_curso,editar_curso
from dashboard.views.estagios import add_estagios, complementar_estagio


urlpatterns = [
    path('',dashboard_instituicao, name='dashboard_instituicao'),
    path('dashboard', dashboard_instituicao, name='dashboard_instituicao'),
    path('home', home, name='home'),
    path('details', details, name='details'),
  
    path('dashboard_estagiario',dashboard_estagiario, name='dashboard_estagiario'),
    path('dashboard_cursos',dashboard_cursos, name='dashboard_cursos'),
    path('cadastrar_cursos',cadastrar_cursos, name='cadastrar_cursos'),
    path('editar_cursos/<int:curso_id>', editar_curso, name='editar_curso'),
    path('deletar_cursos/<int:curso_id>', deletar_curso, name='deletar_curso'),

    path('dashboard_empresa',dashboard_empresa, name='dashboard_empresa'),
    path('detalhes-estagio', detalhes_estagio, name='detalhes_estagio'),
    path('cadastrar-empresa', cadastrar_empresa, name='cadastrar_empresa'),
    path('cadastrar_estagiario', cadastrar_estagiario, name='cadastrar_estagiario'),
    path('add-estagio', add_estagios, name='add_estagio'),
    path('detalhes-estagio', detalhes_estagio, name='detalhes_estagio'),
    path('complementar-estagio', complementar_estagio, name='complementar_estagio'),
    path('importar-pdf', importar_pdf, name='importar_pdf'),
    path('parse-sections', parse_sections, name='parse_sections'),
    path('buscar-cep', buscar_cep, name='buscar_cep'),
    path('validate_cnpj', validate_cnpj, name='validate_cnpj'),
    path('complementar-estagio', complementar_estagio, name='complementar_estagio'),    
]
