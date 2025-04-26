from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
import os
from .forms import CoordenadorCadastroForm
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

    
def visualizar_termo(request, pdf_nome):
    # Caminho completo do arquivo
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT, pdf_nome)

    # Verifique se o arquivo existe
    if os.path.exists(caminho_arquivo):
        try:
            # Abre o arquivo para leitura
            arquivo = open(caminho_arquivo, 'rb')
            # Retorna o arquivo como resposta
            return FileResponse(arquivo, content_type='application/pdf')
        except Exception as e:
            # Caso ocorra um erro, ele será capturado
            raise Http404(f"Erro ao abrir o arquivo: {str(e)}")
    else:
        # Caso o arquivo não exista, levanta uma exceção
        raise Http404("Arquivo não encontrado")