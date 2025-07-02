from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from mais_estagio.forms import OrientadorCadastroForm
from allauth.account.forms import ResetPasswordForm


@login_required
@user_passes_test(lambda u: hasattr(u, "coordenadorextensao") and u.coordenadorextensao)
def cadastro_orientador(request):
    coordenador = getattr(request.user, "coordenadorextensao", None)
    if not coordenador or not coordenador.instituicao:
        messages.error(request, "Instituição do coordenador não encontrada.")
        return redirect("dashboard_instituicao")

    if request.method == "POST":
        form = OrientadorCadastroForm(request.POST, coordenador=coordenador)
        if form.is_valid():
            try:
                user, orientador = form.save()
                # Envia e-mail de redefinição de senha
                reset_form = ResetPasswordForm({'email': user.email})
                if reset_form.is_valid():
                    reset_form.save(request=request)
                messages.success(request, "Orientador cadastrado com sucesso! Um e-mail foi enviado para definir a senha.")
                return redirect("dashboard_instituicao")
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar orientador: {e}")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = OrientadorCadastroForm(coordenador=coordenador)

    return render(request, "orientador/cadastro_orientador.html", {"form": form})