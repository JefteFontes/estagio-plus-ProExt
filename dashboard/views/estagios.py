from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagioCadastroForm
from ..models import Empresa, Estagio


@login_required
def add_estagios(request):
    if request.method == "POST":
        form = EstagioCadastroForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            form.save()  # Salva o Estágio no banco de dados
            messages.success(request, "Estágio cadastrado com sucesso!")
            return redirect(
                "dashboard_instituicao"
            )  # Redireciona para a página de sucesso
        else:
            print("Formulário inválido")
            print(
                form.errors
            )  # Exibe erros no console, caso o formulário não seja válido
    else:
        form = EstagioCadastroForm()  # Cria um formulário vazio para GET

    # voltar para a pagina de dashboard
    return render(request, "add_estagios.html", {"form": form})


def detalhes_estagio(request):
    selected = request.GET.get("selected")
    if not selected:
        return JsonResponse({"error": 'Parâmetro "selected" ausente.'}, status=400)

    estagio = get_object_or_404(Estagio, id=selected)
    return render(request, "details.html", {"estagio": estagio})


@login_required
def complementar_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)

    if request.method == "POST":
        form = EstagioCadastroForm(request.POST, instance=estagio)
        if form.is_valid():
            form.save()
            messages.success(request, "Estágio cadastrado com sucesso!")
            return redirect("dashboard_instituicao")
    else:
        form = EstagioCadastroForm(instance=estagio)

    return render(
        request, "complementar_estagio.html", {"form": form, "estagio": estagio}
    )
