from django.contrib import admin
from . import models


@admin.register(models.Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('rua', 'numero', 'bairro', 'cidade', 'estado', 'cep')
    search_fields = ('rua', 'bairro', 'cidade', 'estado', 'cep')


@admin.register(models.Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'razao_social', 'email', 'endereco')
    search_fields = ('nome', 'cnpj', 'razao_social')
    list_filter = ('endereco__cidade', 'endereco__estado')


@admin.register(models.Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'telefone', 'endereco')
    search_fields = ('nome', 'cnpj', 'email')
    list_filter = ('endereco__cidade', 'endereco__estado')


@admin.register(models.Estagiario)
class EstagiarioAdmin(admin.ModelAdmin):
    list_display = ('primeiro_nome', 'sobrenome', 'cpf', 'matricula', 'email', 'status', 'instituicao')
    search_fields = ('primeiro_nome', 'sobrenome', 'cpf', 'matricula', 'email')
    list_filter = ('instituicao', 'status', 'endereco__cidade')


@admin.register(models.CoordenadorExtensao)
class CoordenadorExtensaoAdmin(admin.ModelAdmin):
    list_display = ('primeiro_nome', 'sobrenome', 'cpf', 'email', 'instituicao')
    search_fields = ('primeiro_nome', 'sobrenome', 'cpf', 'email')
    list_filter = ('instituicao',)


@admin.register(models.Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('primeiro_nome', 'sobrenome', 'cpf', 'email', 'cargo', 'empresa')
    search_fields = ('primeiro_nome', 'sobrenome', 'cpf', 'email', 'cargo')
    list_filter = ('empresa',)


@admin.register(models.Estagio)
class EstagioAdmin(admin.ModelAdmin):
    list_display = ('area', 'bolsa_estagio', 'status', 'data_inicio', 'data_fim', 'turno', 'estagiario', 'supervisor', 'empresa', 'instituicao')
    search_fields = ('area', 'estagiario__primeiro_nome', 'supervisor__primeiro_nome', 'empresa__nome', 'instituicao__nome')
    list_filter = ('status', 'turno', 'empresa', 'instituicao', 'data_inicio', 'data_fim')
    date_hierarchy = 'data_inicio'
