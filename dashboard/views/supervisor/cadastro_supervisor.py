from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from dashboard.models import Empresa
from dashboard.forms import SupervisorCadastroForm
from allauth.account.forms import ResetPasswordForm


@login_required
@user_passes_test(lambda u: hasattr(u, "coordenadorextensao") and u.coordenadorextensao)
def cadastro_supervisor(request, empresa_id):
    coordenador = getattr(request.user, "coordenadorextensao", None)
    empresa = get_object_or_404(Empresa, id=empresa_id, instituicao=coordenador.instituicao)
    if request.method == "POST":
        form = SupervisorCadastroForm(request.POST)
        # Defina o queryset do campo empresa ANTES de validar o form!
        form.fields["empresa"].queryset = Empresa.objects.filter(id=empresa.id)
        if form.is_valid():
            user, supervisor = form.save(commit=False)
            supervisor.empresa = empresa
            supervisor.save()
            # Envio de e-mail redefinir senha (igual orientador)
            reset_form = ResetPasswordForm({'email': user.email})
            if reset_form.is_valid():
                reset_form.save(request=request)
            messages.success(request, "Supervisor cadastrado com sucesso! Um e-mail foi enviado para definir a senha.")
            return redirect("dashboard_empresa")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = SupervisorCadastroForm(initial={"empresa": empresa})
        form.fields["empresa"].queryset = Empresa.objects.filter(id=empresa.id)

    return render(request, "supervisor/cadastro_supervisor.html", {"form": form, "empresa": empresa})