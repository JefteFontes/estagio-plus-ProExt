import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from mais_estagio.models import Aluno, Estagio, StatusChoices
from mais_estagio.views.estagios import (
    estagio_duracao,
    estagio_falta_dias,
    verificar_relatorios_pendentes,
)


@login_required
def estagio_andamento(request):
    try:
        aluno_logado = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(request, "Seu perfil de aluno não foi encontrado. Por favor, contate o suporte.")
        return redirect("login")

    estagio = Estagio.objects.filter(
        estagiario=aluno_logado,
        status=StatusChoices.em_andamento
    ).first()

    duracao = "N/A"
    tempo_falta_display = ""
    relatorios_pendentes = []
    documento_url = None

    if estagio:
        duracao = estagio_duracao(estagio)
        
        tempo_falta_bruto_str = estagio_falta_dias(estagio) 
        
        if tempo_falta_bruto_str == "0 dias":
            if estagio.data_fim <= datetime.date.today():
                 tempo_falta_display = f"Encerrado há {tempo_falta_bruto_str}"
            else:
                 tempo_falta_display = f"Faltam {tempo_falta_bruto_str}"
        elif tempo_falta_bruto_str:
            if estagio.data_fim < datetime.date.today():
                tempo_falta_display = f"Encerrado há {tempo_falta_bruto_str}"
            else:
                tempo_falta_display = f"Faltam {tempo_falta_bruto_str}"
        else:
            tempo_falta_display = "Tempo indisponível"
        
        relatorios_pendentes = verificar_relatorios_pendentes(estagio)
        if estagio.pdf_termo:
            documento_url = estagio.pdf_termo.url

    context = {
        "estagio": estagio,
        "duracao": duracao,
        "tempo_falta": tempo_falta_display,
        "relatorios_pendentes": relatorios_pendentes,
        "documento_url": documento_url,
    }
    
    return render(request, "aluno/estagio_andamento.html", context)