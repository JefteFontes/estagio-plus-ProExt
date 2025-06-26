from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mais_estagio.forms import CoordenadorEditForm
from mais_estagio.models import CoordenadorExtensao


@login_required
def editar_perfil(request):
    coordenador = get_object_or_404(CoordenadorExtensao, user=request.user)

    if request.method == "POST":
        form = CoordenadorEditForm(
            request.POST, request.FILES, coordenador=coordenador, instance=coordenador
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Seu perfil foi atualizado com sucesso!")
            return redirect(
                "dashboard_instituicao"
            )  # Redirect to the dashboard or another page
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CoordenadorEditForm(coordenador=coordenador, instance=coordenador)

    return render(request, "edit_profile.html", {"form": form})
