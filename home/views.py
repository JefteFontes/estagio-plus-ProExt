from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CoordenadorCadastroForm, Instituicao

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
            return redirect('/login/')  # Redireciona para a página de login após o cadastro
    else:
        form = CoordenadorCadastroForm()
    return render(request, 'cadastro/cadastrar_instituicao.html', {'form': form})

from django.shortcuts import get_object_or_404

def editar_instituicao(request, instituicao):
    instituicao = get_object_or_404(CoordenadorCadastroForm, id=instituicao)

    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST, instance=instituicao)
        if form.is_valid():
            form.save()
            return redirect('dashboard_instituicao')
    else:
        form = CoordenadorCadastroForm(instance=instituicao)
    return render(request, 'cadastro/cadastrar_instituicao.html', {'form': form, 'instituicao': instituicao})