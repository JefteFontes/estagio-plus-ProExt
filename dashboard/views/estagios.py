import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor, RelatorioEstagio


def formatar_duracao(diferenca):
    partes = [
        f"{diferenca.years} ano(s)" if diferenca.years else "",
        f"{diferenca.months} mes(es)" if diferenca.months else "",
        f"{diferenca.days} dia(s)" if diferenca.days or not (diferenca.years or diferenca.months) else "",
    ]
    return ", ".join([p for p in partes if p])


def estagio_duracao(estagio):
    diferenca = relativedelta(estagio.data_fim, estagio.data_inicio)
    return formatar_duracao(diferenca)


def estagio_falta_dias(estagio):
    hoje = datetime.date.today()
    if estagio.data_fim < hoje:
        return "0 dias"  # Estágio já finalizado
    diferenca = relativedelta(estagio.data_fim, hoje)
    return formatar_duracao(diferenca)


def verificar_relatorios_pendentes(estagio):
    hoje = datetime.date.today()
    relatorios = []

    # Termo de compromisso
    if hoje >= estagio.data_inicio:
        relatorios.append({
            "tipo": "Termo de Compromisso",
            "data_prevista": estagio.data_inicio
        })

    # Relatórios semestrais
    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append({
            "tipo": "Relatório Semestral",
            "data_prevista": data
        })
        data += relativedelta(months=6)

    # Relatórios finais
    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append({
                "tipo": tipo,
                "data_prevista": estagio.data_fim
            })

    return relatorios


def processar_form_estagio(request, estagio=None, template="add_estagios.html"):
    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, instance=estagio)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágio salvo com sucesso!")
            return redirect("dashboard_instituicao")
        else:
            messages.error(request, "Erro ao salvar estágio.")
    else:
        form = EstagioCadastroForm(instance=estagio)

    return render(request, template, {"form": form, "estagio": estagio})


@login_required
def add_estagios(request):
    return processar_form_estagio(request)


@login_required
def editar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    return processar_form_estagio(request, estagio)


@login_required
def complementar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    return processar_form_estagio(request, estagio, template="complementar_estagio.html")


def detalhes_estagio(request):
    selected = request.GET.get("selected")
    if not selected:
        return JsonResponse({"error": 'Parâmetro "selected" ausente.'}, status=400)

    estagio = get_object_or_404(Estagio, id=selected)
    duracao = estagio_duracao(estagio)
    tempo_falta = estagio_falta_dias(estagio)
    relatorios_pendentes = verificar_relatorios_pendentes(estagio)

    return render(request, 'details.html', {
        'estagio': estagio,
        'duracao': duracao,
        'tempo_falta': tempo_falta,
        'relatorios_pendentes': relatorios_pendentes
    })


def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(
            empresa_id=empresa_id
        ).values("id", "primeiro_nome", "sobrenome")
        return JsonResponse(list(supervisores), safe=False)
    return JsonResponse([], safe=False)
