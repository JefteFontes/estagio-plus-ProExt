import traceback
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
import os
from .forms import CoordenadorCadastroForm, AlunoCadastroForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.forms import ResetPasswordForm
from dashboard.models import Cursos, Estagiario
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

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


def cadastro_aluno(request):
    if request.method == "POST":
        try:
            form = AlunoCadastroForm(request.POST)
            if form.is_valid():
                estagiario = form.save()
                messages.success(
                    request,
                    "Cadastro do aluno realizado com sucesso! Aguarde a validação do coordenador para obter o acesso ao sistema.",
                )
                return redirect("/login/")
            else:
                print("Formulário inválido:")
                print(form.errors)
                messages.error(
                    request,
                    "Houve erros no preenchimento do formulário. Por favor, corrija-os.",
                )
                return render(request, "cadastro/cadastro_aluno.html", {"form": form})
        except Exception as e:
            print("Erro ao processar o formulário POST:")
            traceback.print_exc()
            messages.error(
                request, f"Ocorreu um erro inesperado ao cadastrar o aluno: {str(e)}"
            )
            return render(request, "cadastro/cadastro_aluno.html", {"form": form})
    else:
        try:
            form = AlunoCadastroForm()
        except Exception as e:
            print("Erro ao instanciar o formulário GET:")
            traceback.print_exc()
            form = None
            messages.error(
                request, f"Erro ao carregar o formulário de cadastro: {str(e)}"
            )

    return render(request, "cadastro/cadastro_aluno.html", {"form": form})


@login_required
@user_passes_test(lambda u: hasattr(u, 'coordenadorextensao'))
def aprovar_estagiario(request, estagiario_id):
    estagiario = Estagiario.objects.get(id=estagiario_id)
    
    if not estagiario.user:
        # Cria o usuário no sistema via Allauth
        user = User.objects.create_user(
            username=estagiario.nome_completo,
            email=estagiario.email,
            password=estagiario.cpf  # Senha inicial = CPF
        )
        
        # Configura o email como verificado no Allauth
        EmailAddress.objects.create(
            user=user,
            email=estagiario.email,
            primary=True,
            verified=True
        )
        
        estagiario.user = user
        estagiario.status = True
        print("Criando usuário...")
        estagiario.save()
        
        messages.success(request, f"Acesso ativado para {estagiario.nome_completo}")
    else:
        messages.warning(request, "Este estagiário já possui acesso ao sistema")
    
    return redirect("dashboard_estagiario")