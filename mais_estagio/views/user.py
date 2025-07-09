from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mais_estagio.forms import CoordenadorEditForm
from mais_estagio.models import CoordenadorExtensao

@login_required
def editar_perfil(request):
    if hasattr(request.user, 'aluno') and request.user.aluno:
        return redirect('editar_estagiario', estagiario_id=request.user.aluno.id)

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
            )
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = CoordenadorEditForm(coordenador=coordenador, instance=coordenador)

    return render(request, "edit_profile.html", {"form": form})