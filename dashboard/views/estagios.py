import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor, RelatorioEstagio
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings


def formatar_duracao(diferenca):
    partes = [
        f"{diferenca.years} ano(s)" if diferenca.years else "",
        f"{diferenca.months} mes(es)" if diferenca.months else "",
        (
            f"{diferenca.days} dia(s)"
            if diferenca.days or not (diferenca.years or diferenca.months)
            else ""
        ),
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
        relatorios.append(
            {"tipo": "Termo de Compromisso", "data_prevista": estagio.data_inicio}
        )

    # Relatórios semestrais
    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append({"tipo": "Relatório Semestral", "data_prevista": data})
        data += relativedelta(months=6)

    # Relatórios finais
    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append({"tipo": tipo, "data_prevista": estagio.data_fim})

    return relatorios


def enviar_notificacao_relatorio_atrasado(estagio, request):
    hoje = datetime.date.today()
    relatorios_atrasados = [
        relatorio
        for relatorio in verificar_relatorios_pendentes(estagio)
        if relatorio["data_prevista"] < hoje
    ]

    if not relatorios_atrasados:
        return False
    coordenador_email = request.user.email

    context = {
        "empresa_name": estagio.empresa.empresa_nome,
        "estagiario_name": estagio.estagiario.nome_completo,
        "relatorios_pendentes": relatorios_atrasados,
        "site_name": settings.SITE_NAME,
        "site_url": request.build_absolute_uri("/"),
    }

    email_content = render_to_string("emails/relatorio_notificacao.txt", context)

    send_mail(
        subject=_("Relatório pendente"),
        message=email_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[coordenador_email],
        fail_silently=False,
    )

    return True


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


from ..models import Empresa, Estagio, Supervisor
from dateutil.relativedelta import relativedelta
from dashboard.views.relatorios import verificar_relatorios_pendentes


@login_required
def add_estagios(request):
    return processar_form_estagio(request)
    form = EstagioCadastroForm(user=request.user)

    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Estágio cadastrado com sucesso!")
            return redirect("dashboard_instituicao")

    return render(request, "add_estagios.html", {"form": form})


@login_required
def editar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)

    if request.method == "POST":
        print("Dados do formulário:", request.POST)
        form = EstagioCadastroForm(request.POST, instance=estagio, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágio atualizado com sucesso!")
            return redirect("dashboard_instituicao")
        else:
            messages.error(request, "Erro ao atualizar o estágio. Verifique os dados.")

    form = EstagioCadastroForm(instance=estagio, user=request.user)

    return processar_form_estagio(request, estagio)


@login_required
def complementar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    return processar_form_estagio(
        request, estagio, template="complementar_estagio.html"
    )


def detalhes_estagio(request):
    selected = request.GET.get("selected")
    if not selected:
        return JsonResponse({"error": 'Parâmetro "selected" ausente.'}, status=400)

    estagio = get_object_or_404(Estagio, id=selected)
    duracao = estagio_duracao(estagio)
    tempo_falta = estagio_falta_dias(estagio)
    relatorios_pendentes = verificar_relatorios_pendentes(estagio)
    enviar_notificacao_relatorio_atrasado(estagio, request)

    return render(
        request,
        "details.html",
        {
            "estagio": estagio,
            "duracao": duracao,
            "tempo_falta": tempo_falta,
            "relatorios_pendentes": relatorios_pendentes,
        },
    )


def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(empresa_id=empresa_id).values(
            "id", "nome_completo"
        )
        return JsonResponse(list(supervisores), safe=False)
    return JsonResponse([], safe=False)


def processar_form_estagio(request, estagio, template="add_estagios.html"):
    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, instance=estagio, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágio atualizado com sucesso!")
            return redirect("dashboard_instituicao")
        else:
            messages.error(request, "Erro ao atualizar o estágio. Verifique os dados.")
    else:
        form = EstagioCadastroForm(instance=estagio, user=request.user)

    return render(request, template, {"form": form, "estagio": estagio})


def estagio_duracao(estagio):
    if estagio.data_inicio and estagio.data_fim:
        return (estagio.data_fim - estagio.data_inicio).days
    return None


def estagio_falta_dias(estagio):
    if estagio.data_fim:
        dias_faltando = (estagio.data_fim - datetime.date.today()).days
        return max(dias_faltando, 0)
    return None
