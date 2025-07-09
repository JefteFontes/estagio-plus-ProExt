from django.urls import include, path
from mais_estagio.views.empresa import (
    cadastrar_empresa,
    editar_empresa,
    deletar_empresa,
)
from .views import cadastrar_instituicao
from mais_estagio.views.estagiarios import (
    cadastrar_estagiario,
    editar_estagiario,
    deletar_estagiario,
    estagiario_auto_cadastro,
)
from .views.aluno import cadastro_aluno, estagios_aluno, detalhes_estagio_aluno
from mais_estagio.views.pdfimport import importar_pdf
from mais_estagio.views.estagios import (
    detalhes_estagio,
    get_supervisores,
    editar_estagio,
    add_estagios,
    complementar_estagio,
    download_tceu,
    importar_termo,
)

from home.utils import parse_sections, buscar_cep, validate_cnpj
from mais_estagio.views.home import (
    home,
    details,
    dashboard_instituicao,
    dashboard_empresa,
    dashboard_estagiario,
    dashboard_cursos,
    cadastrar_cursos,
    deletar_curso,
    editar_curso,
)
from mais_estagio.views.user import editar_perfil
from django.conf import settings
from django.conf.urls.static import static
from mais_estagio.views.relatorios import  relatorios, verificar_relatorios_pendentes, importar_termo_relatorio
from mais_estagio.views.personalizados import dashboard_personalizados, relatorio_personalidizado
from mais_estagio.views.orientador import cadastro_orientador, dashboard_orientador , relatorios_orientador
from mais_estagio.views.supervisor import cadastro_supervisor, dashboard_supervisor, relatorios_supervisor


urlpatterns = [
    path("", dashboard_instituicao, name="dashboard_instituicao"),
    path("dashboard", dashboard_instituicao, name="dashboard_instituicao"),
    path("instituicao/cadastro", cadastrar_instituicao,name="cadastro_instituicao"),
    path('cadastro/', cadastro_aluno, name='cadastro_aluno'),
    path('dashboard/estagios-aluno/', estagios_aluno, name='estagios_aluno'),
    path('dashboard/estagio/<int:pk>/', detalhes_estagio_aluno, name='detalhes_estagio_aluno'),
    path("home", home, name="home"),
    path("details", details, name="details"),
    path("dashboard_estagiario", dashboard_estagiario, name="dashboard_estagiario"),
    path("dashboard_cursos", dashboard_cursos, name="dashboard_cursos"),
    path("cadastrar_cursos", cadastrar_cursos, name="cadastrar_cursos"),
    path("editar_cursos/<int:curso_id>", editar_curso, name="editar_curso"),
    path("deletar_curso/<int:curso_id>", deletar_curso, name="deletar_curso"),
    path("detalhes-estagio", detalhes_estagio, name="detalhes_estagio"),
    path('estagio/<int:estagio_id>/download-tceu/', download_tceu, name='download_tceu'),
    path("relatorios/", relatorios, name="dashboard_relatorios"),
    path(
        "estagio/<int:estagio_id>/relatorios/",
        verificar_relatorios_pendentes,
        name="relatorios_pendentes",
    ),
    path("dashboard_personalizados/", dashboard_personalizados, name="dashboard_personalizados"),
    path("relatorio_personalizado/", relatorio_personalidizado, name="relatorio_personalizado"),
    
    path("cadastrar-empresa", cadastrar_empresa, name="cadastrar_empresa"),
    path("dashboard_empresa", dashboard_empresa, name="dashboard_empresa"),
    path("editar_empresa/<int:empresa_id>", editar_empresa, name="editar_empresa"),
    path("deletar_empresa/<int:empresa_id>", deletar_empresa, name="deletar_empresa"),
    path("get_supervisores/", get_supervisores, name="get_supervisores"),


    path('cadastrar_estagiario', cadastrar_estagiario, name='cadastrar_estagiario'),
    path('editar_estagiario/<int:estagiario_id>', editar_estagiario, name='editar_estagiario'),
    path('deletar_estagiario/<int:estagiario_id>', deletar_estagiario, name='deletar_estagiario'),
    path('estagiario/cadastro/<uuid:token>/', estagiario_auto_cadastro, name='estagiario_auto_cadastro'),

    path("cadastrar_orientador/", cadastro_orientador, name="cadastrar_orientador"),
    path("dashboard_orientador/", dashboard_orientador, name="dashboard_orientador"),
    path("relatorios_orientador/", relatorios_orientador, name="relatorios_orientador"),

    path("cadastrar_supervisor/<int:empresa_id>/", cadastro_supervisor, name="cadastrar_supervisor"),
    path("dashboard_supervisor/", dashboard_supervisor, name="dashboard_supervisor"),
    path("relatorios_supervisor/", relatorios_supervisor, name="relatorios_supervisor"),
    

    path('add-estagio', add_estagios, name='add_estagio'),
    path('detalhes-estagio', detalhes_estagio, name='detalhes_estagio'),
    path('complementar-estagio', complementar_estagio, name='complementar_estagio'), 
    path('editar_estagio/<int:estagio_id>', editar_estagio, name='editar_estagio'),   


    path('estagio/<int:estagio_id>/importar-termo/', importar_termo, name='importar_termo'),
    path('parse-sections', parse_sections, name='parse_sections'),
    path('buscar-cep', buscar_cep, name='buscar_cep'),
    path('validate_cnpj', validate_cnpj, name='validate_cnpj'),


    path('editar-perfil/', editar_perfil, name='editar_perfil'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
