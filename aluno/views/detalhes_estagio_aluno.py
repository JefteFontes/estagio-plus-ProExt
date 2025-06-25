from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from aluno.models import Aluno
from dashboard.models import Estagio
from dashboard.views.estagios import (
    estagio_duracao,
    estagio_falta_dias,
    verificar_relatorios_pendentes,
)


@login_required
def detalhes_estagio_aluno(request, pk):
    try:
        aluno_logado = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(request, "Seu perfil de aluno não foi encontrado.")
        return redirect("profile_redirect")

    estagio = get_object_or_404(Estagio, pk=pk)

    if estagio.estagiario != aluno_logado:
        messages.error(
            request, "Você não tem permissão para visualizar os detalhes deste estágio."
        )
        return redirect("estagios_aluno")

    duracao = estagio_duracao(estagio)
    tempo_falta = estagio_falta_dias(estagio)
    relatorios_pendentes = verificar_relatorios_pendentes(estagio)

    documento_url = None
    if estagio.pdf_termo:
        documento_url = estagio.pdf_termo.url

    context = {
        "estagio": estagio,
        "duracao": duracao,
        "tempo_falta": tempo_falta,
        "relatorios_pendentes": relatorios_pendentes,
        "documento_url": documento_url,
    }
    return render(request, "aluno/detalhes_estagio_aluno.html", context)
