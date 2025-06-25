from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import FileResponse, Http404
import os

from dashboard.forms import CoordenadorCadastroForm
from dashboard.models import Aluno
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from dashboard.models import Cursos
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from home.utils import ativar_acesso_estagiario


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
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT, pdf_nome)

    if os.path.exists(caminho_arquivo):
        try:
            arquivo = open(caminho_arquivo, "rb")
            return FileResponse(arquivo, content_type="application/pdf")
        except Exception as e:
            raise Http404(f"Erro ao abrir o arquivo: {str(e)}")
    else:
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

@login_required
def profile_redirect(request):
    user = request.user

    if hasattr(user, "coordenadorextensao") and user.coordenadorextensao:
        return redirect("dashboard_instituicao")

    if hasattr(user, "aluno") and user.aluno:
        return redirect("estagios_aluno")

    messages.warning(
        request,
        "Seu perfil não está associado a um tipo de usuário válido. Contate o Coordenador.",
    )
    return redirect('/login/')