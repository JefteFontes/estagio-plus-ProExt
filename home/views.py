import traceback
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import FileResponse, Http404
import os

from aluno.models import Aluno
from .forms import CoordenadorCadastroForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from allauth.account.forms import ResetPasswordForm
from dashboard.models import Cursos
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from dashboard.views.utils import ativar_acesso_estagiario


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect("/accounts/profile/")
    return render(request, "home/home.html")


def pre_cadastro(request):
    return render(request, "cadastro/pre_cadastro.html")


def load_cursos(request):
    instituicao_id = request.GET.get("instituicao_id")
    cursos = Cursos.objects.filter(instituicao_id=instituicao_id).order_by("nome_curso")
    return JsonResponse(list(cursos.values("id", "nome_curso")), safe=False)





def editar_instituicao(request, instituicao):
    instituicao = get_object_or_404(CoordenadorCadastroForm, id=instituicao)

    if request.method == "POST":
        form = CoordenadorCadastroForm(
            request.POST, request.FILES, instance=instituicao
        )
        if form.is_valid():
            form.save()
            return redirect("dashboard_instituicao")
    else:
        form = CoordenadorCadastroForm(instance=instituicao)
    return render(
        request,
        "cadastro/cadastrar_instituicao.html",
        {"form": form, "instituicao": instituicao},
    )


def visualizar_termo(request, pdf_nome):
    # Caminho completo do arquivo
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT, pdf_nome)

    # Verifique se o arquivo existe
    if os.path.exists(caminho_arquivo):
        try:
            # Abre o arquivo para leitura
            arquivo = open(caminho_arquivo, "rb")
            # Retorna o arquivo como resposta
            return FileResponse(arquivo, content_type="application/pdf")
        except Exception as e:
            # Caso ocorra um erro, ele será capturado
            raise Http404(f"Erro ao abrir o arquivo: {str(e)}")
    else:
        # Caso o arquivo não exista, levanta uma exceção
        raise Http404("Arquivo não encontrado")


@login_required
@user_passes_test(lambda u: u.is_staff or hasattr(u, "coordenadorextensao"))
def ativar_acesso_estagiario_view(request, estagiario_id):
    estagiario = get_object_or_404(Aluno, pk=estagiario_id)

    if request.method == "POST":
        success, message = ativar_acesso_estagiario(request, estagiario)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect("dashboard_estagiario")
    else:
        messages.error(request, "Requisição inválida para ativação de usuário.")
        return redirect("dashboard_estagiario")
