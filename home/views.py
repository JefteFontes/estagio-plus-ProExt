from django.shortcuts import render, redirect
from .forms import CoordenadorCadastroForm
from django.contrib import messages

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('/accounts/profile/')
    return render(request, 'home/home.html')


def cadastrar_instituicao(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            user, coordenador = form.save()
            messages.success(request, 'Instituição cadastrada com sucesso!')
            return redirect('/login/')  # Redireciona para a página de login após o cadastro
    else:
        form = CoordenadorCadastroForm()
    return render(request, 'cadastro/cadastrar_instituicao.html', {'form': form})
