from django.urls import path
from .views import cadastrar_instituicao

urlpatterns = [
    path("cadastro/", cadastrar_instituicao,name="cadastro_instituicao"),
]
