from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mais_estagio.models import Aluno, Estagio


@login_required
def estagios_aluno(request):
    aluno = None
    estagios = []

    try:
        aluno = Aluno.objects.get(user=request.user)
        estagios = Estagio.objects.filter(estagiario=aluno).order_by("-data_inicio")
    except Aluno.DoesNotExist:
        messages.error(
            request,
            "Seu perfil de aluno não foi encontrado. Por favor, contate o administrador.",
        )
        return redirect("/login/")

    context = {
        "aluno": aluno,
        "estagios": estagios,
    }
    return render(request, "aluno/estagios_aluno.html", context)