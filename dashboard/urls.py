from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_instituicao, name='dashboard_instituicao'),
    path('cadastrar-estagiario', views.cadastrar_estagiario, name='cadastrar_estagiario'),
    path('cadastrar-empresa', views.cadastrar_empresa, name='cadastrar_empresa'),
]
