from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import FileResponse, Http404
import os

from mais_estagio.forms import CoordenadorCadastroForm
from mais_estagio.models import Aluno
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from allauth.account.forms import ResetPasswordForm
from mais_estagio.models import Cursos,Aluno
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from home.utils import ativar_acesso_estagiario
import traceback
from django.template.loader import render_to_string
from django.core.mail import send_mail

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


def cadastrar_instituicao(request):
    if request.method == "POST":
        try:
            form = CoordenadorCadastroForm(request.POST, request.FILES)
        except Exception as e:
            print("Erro ao instanciar o formulário:")
            traceback.print_exc()
            messages.error(request, f"Erro ao processar o formulário: {str(e)}")
            return render(
                request, "cadastro/cadastrar_instituicao.html", {"form": None}
            )

        if form.is_valid():
            try:
                user, coordenador = form.save()
            except Exception as e:
                print("Erro ao salvar o formulário:")
                traceback.print_exc()
                messages.error(request, f"Erro ao salvar o cadastro: {str(e)}")
                return render(
                    request, "cadastro/cadastrar_instituicao.html", {"form": form}
                )

            try:
                reset_form = ResetPasswordForm({"email": user.email})
                if reset_form.is_valid():
                    reset_form.save(request=request)
                    messages.success(
                        request,
                        "Cadastro realizado! Verifique seu email para redefinir a senha.",
                    )
                else:
                    messages.warning(
                        request,
                        "Cadastro realizado, mas houve um erro ao enviar o email de redefinição.",
                    )
            except Exception as e:
                print("Erro ao enviar email de redefinição de senha:")
                traceback.print_exc()
                messages.warning(
                    request,
                    "Cadastro realizado, mas falha ao preparar redefinição de senha.",
                )

            try:
                context = {
                    "user_name": user.get_full_name() or user.username,
                    "site_name": settings.SITE_NAME,
                    "site_url": request.build_absolute_uri("/"),
                }

                email_content = render_to_string(
                    "emails/cadastro_concluido.txt", context
                )
                send_mail(
                    subject=_("Bem-vindo ao ") + settings.SITE_NAME,
                    message=email_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print("Erro ao enviar email de boas-vindas:")
                traceback.print_exc()
                messages.warning(
                    request,
                    "Cadastro feito, mas erro ao enviar o email de boas-vindas.",
                )

            messages.success(request, "Instituição cadastrada com sucesso!")
            return redirect("/login/")
        else:
            print("Formulário inválido:")
            print(form.errors)
            messages.error(request, "Corrija os erros abaixo.")
            return render(
                request, "cadastro/cadastrar_instituicao.html", {"form": form}
            )
    else:
        try:
            form = CoordenadorCadastroForm()
        except Exception as e:
            print("Erro ao instanciar o formulário GET:")
            traceback.print_exc()
            form = None
            messages.error(request, f"Erro ao carregar o formulário: {str(e)}")

    return render(request, "cadastro/cadastrar_instituicao.html", {"form": form})


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

@login_required
@user_passes_test(lambda u: u.is_staff or hasattr(u, 'coordenadorextensao'))
def ativar_acesso_estagiario_view(request, estagiario_id):
    estagiario = get_object_or_404(Aluno, pk=estagiario_id)

    if request.method == "POST":
        success, message = ativar_acesso_estagiario(request, estagiario)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('dashboard_estagiario')
    else:
        messages.error(request, "Requisição inválida para ativação de usuário.")
        return redirect("dashboard_estagiario")


@login_required
def profile_redirect(request):
    user = request.user

    if hasattr(user, "coordenadorextensao") and user.coordenadorextensao:
        return redirect("dashboard_instituicao")

    if hasattr(user, "aluno") and user.aluno:
        return redirect("estagio_andamento")

    if hasattr(user, "orientador") and user.orientador:
        return redirect("dashboard_orientador")

    if hasattr(user, "supervisor") and user.supervisor:
        return redirect("dashboard_supervisor")

    messages.warning(
        request,
        "Seu perfil não está associado a um tipo de usuário válido. Contate o Coordenador.",
    )
    return redirect('login')
