from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def profile_redirect(request):
    user = request.user

    if hasattr(user, "coordenadorextensao") and user.coordenadorextensao:
        return redirect("dashboard_instituicao")

    if hasattr(user, "aluno") and user.aluno:
        return redirect("dashboard_aluno")

    messages.warning(
        request,
        "Seu perfil não está associado a um tipo de usuário válido. Contate o Coordenador.",
    )
    return redirect('/login/')
