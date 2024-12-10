from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_instituicao, name='dashboard_instituicao'),
    path('detalhes-estagio', views.detalhes_estagio, name='detalhes_estagio'),
    path('details', views.details, name='details'),
    path('cadastrar-estagiario', views.cadastrar_estagiario, name='cadastrar_estagiario'),
    path('cadastrar-empresa', views.cadastrar_empresa, name='cadastrar_empresa'),
    path('add-estagios', views.add_estagios, name='add_estagios'),
]
