from django.contrib import admin
from .models import Aluno


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "cpf",
        "matricula",
        "email",
        "status",
        "instituicao",
    )
    search_fields = ("nome", "cpf", "matricula", "email")
    list_filter = ("instituicao", "status", "endereco__cidade")
