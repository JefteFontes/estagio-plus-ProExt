from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.models import Estagiario 

@login_required
def dashboard_aluno(request):
    try:
        
        estagiario = Estagiario.objects.get(user=request.user)
    except Estagiario.DoesNotExist:
        messages.error(request, "Seu perfil de estagiário não foi encontrado. Por favor, contate o administrador.")
        return redirect('/login/') 

    context = {
        'estagiario': estagiario,
    }
    return render(request, 'dashboard_aluno.html', context)