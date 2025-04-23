import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor
from dateutil.relativedelta import relativedelta
from dashboard.views.relatorios import verificar_relatorios_pendentes



@login_required
def add_estagios(request):
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
        ).values("id", "nome_completo")
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
