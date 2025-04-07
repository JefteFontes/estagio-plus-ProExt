from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from dashboard.models import CoordenadorExtensao, Estagio
from ..forms import EstagiarioCadastroForm,Estagiario

@login_required
def cadastrar_estagiario(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    if request.method == "POST":
        form = EstagiarioCadastroForm(coordenador=coordenador, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágiario cadastrado com sucesso!")
            return redirect("dashboard_estagiario")
    else:
        form = EstagiarioCadastroForm()     

    return render(request, 'cadastrar_estagiario.html', {'form': form})

def editar_estagiario(request, estagiario_id):
    estagiario = get_object_or_404(Estagiario, id=estagiario_id)
    
    if request.method == 'POST':
        form = EstagiarioCadastroForm(request.POST, instance=estagiario)
        if form.is_valid():
            form.save()
            return redirect('dashboard_estagiario')
    else:
        form = EstagiarioCadastroForm(instance=estagiario)
    return render(request, 'cadastrar_estagiario.html', {'form': form, 'estagiario': estagiario})


def deletar_estagiario(request, estagiario_id):
    estagiario = get_object_or_404(Estagiario, id=estagiario_id)
    #verificar se der algum erro
    if Estagio.objects.filter(estagiario=estagiario).exists():
        messages.error(request, 'O estagiario possui estagios vinculados e nao pode ser deletado.')
        return redirect('dashboard_estagiario')
    else:
        estagiario.delete()
        return redirect('dashboard_estagiario')
