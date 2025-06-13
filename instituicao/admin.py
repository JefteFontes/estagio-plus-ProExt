from django.contrib import admin
from .models import Instituicao

@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "email", "telefone", "endereco")
    search_fields = ("nome", "cnpj", "email")
    list_filter = ("endereco__cidade", "endereco__estado")