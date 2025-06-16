from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from aluno.models import Aluno


@login_required
def dashboard_aluno(request):
    try:
        aluno = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        messages.error(
            request,
            "Seu perfil de aluno não foi encontrado. Por favor, contate o administrador.",
        )
        return redirect("/login/")

    context = {
        "estagiario": aluno,
    }
    return render(request, "aluno/dashboard_aluno.html", context)
