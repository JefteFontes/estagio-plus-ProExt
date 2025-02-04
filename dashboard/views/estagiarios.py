from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from dashboard.models import CoordenadorExtensao
from ..forms import EstagiarioCadastroForm


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

    return render(request, "cadastrar_estagiario.html", {"form": form})
