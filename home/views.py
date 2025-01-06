from django.shortcuts import render, redirect
from .forms import CoordenadorCadastroForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_instituicao')

    return render(request, 'home/home.html')


def cadastrar_instituicao(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            user, coordenador = form.save()
            return redirect('/login/')  # Redireciona para a página de login após o cadastro
    else:
        form = CoordenadorCadastroForm()
    return render(request, 'cadastro/cadastrar_instituicao.html', {'form': form})
