from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CoordenadorCadastroForm, Instituicao
from django.contrib import messages
from django.contrib.auth import get_user_model
from allauth.account.forms import ResetPasswordForm

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('/accounts/profile/')
    return render(request, 'home/home.html')


def cadastrar_instituicao(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            try:
                user, coordenador = form.save()
                reset_form = ResetPasswordForm({'email': user.email})
                if reset_form.is_valid():
                    reset_form.save(request=request)
                    messages.success(request, 'Cadastro realizado! Verifique seu email para redefinir a senha.')
                else:
                    messages.warning(request, 'Cadastro realizado, mas houve um erro ao enviar o email de redefinição.')
                return redirect('/login/')
            except Exception as e:
                messages.error(request, f'Erro no cadastro: {str(e)}')
                return redirect('cadastro_instituicao')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
            messages.error(request, form.errors)
            return redirect('cadastro_instituicao')
    else:
        form = CoordenadorCadastroForm()
    
    return render(request, 'cadastro/cadastrar_instituicao.html', {'form': form})


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