import datetime
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio, Supervisor
from dateutil.relativedelta import relativedelta



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

    return render(request, "add_estagios.html", {"form": form, "estagio": estagio})


def detalhes_estagio(request):
    selected = request.GET.get("selected")
    if not selected:
        return JsonResponse({"error": 'Parâmetro "selected" ausente.'}, status=400)

    estagio = get_object_or_404(Estagio, id=selected)
    duracao = estagio_duracao(request, selected)
    tempo_falta = estagio_falta_dias(request, selected)

    return render(request, 'details.html', {
        'estagio': estagio, 
        'duracao': duracao, 
        'tempo_falta': tempo_falta
    })
@login_required
def complementar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)

    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, instance=estagio)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágio cadastrado com sucesso!")
            return redirect("dashboard_instituicao")
    else:
        form = EstagioCadastroForm(instance=estagio)

    return render(request, 'complementar_estagio.html', {'form': form, 'estagio': estagio})


def formatar_duracao(diferenca):
    partes = []
    
    if diferenca.years > 0:
        partes.append(f"{diferenca.years} ano(s)")
    if diferenca.months > 0:
        partes.append(f"{diferenca.months} mes(es)")
    if diferenca.days > 0 or not partes:  # Se não houver anos/meses, mostrar dias
        partes.append(f"{diferenca.days} dia(s)")

    return ", ".join(partes)  # Retorna apenas os valores não nulos

def estagio_duracao(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    diferenca = relativedelta(estagio.data_fim, estagio.data_inicio)
    return formatar_duracao(diferenca)

def estagio_falta_dias(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
    
    if estagio.data_fim < datetime.date.today():
        messages.error(request, "Prazo de estágio expirado")
        return "faltam 0 dias"  # Estágio já finalizado
        

    diferenca = relativedelta(estagio.data_fim, datetime.date.today())
    return formatar_duracao(diferenca)


def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(empresa_id=empresa_id).values("id", "primeiro_nome","sobrenome")
        return JsonResponse(list(supervisores), safe=False)
    return JsonResponse([], safe=False)