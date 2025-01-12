from django.urls import include, path
from dashboard.views.empresa import cadastrar_empresa
from dashboard.views.estagiarios import cadastrar_estagiario
from dashboard.views.pdfimport import importar_pdf
from dashboard.views.estagios import detalhes_estagio
from dashboard.views.utils import parse_sections, buscar_cep, validate_cnpj
from dashboard.views.home import home, details, dashboard_instituicao
from dashboard.views.estagios import add_estagios, complementar_estagio


urlpatterns = [
    path('',dashboard_instituicao, name='dashboard_instituicao'),
    path('home', home, name='home'),
    path('details', details, name='details'),
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
