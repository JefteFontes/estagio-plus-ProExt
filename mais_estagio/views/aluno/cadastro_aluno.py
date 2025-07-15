import traceback
from django.shortcuts import render, redirect
from django.contrib import messages
from mais_estagio.views.estagiarios import AlunoCadastroForm 

def cadastro_aluno(request):
    if request.method == "POST":
        try:
            form = AlunoCadastroForm(request.POST)
            if form.is_valid():
                if not form.cleaned_data.get('curso'):
                    form.add_error('curso', 'Selecione um curso válido')
                    return render(request, 'cadastro_aluno.html', {'form': form})
                if not form.cleaned_data.get('instituicao'):
                    form.add_error('instituicao', 'Selecione uma instituição válida')
                    return render(request, 'cadastro_aluno.html', {'form': form})
                
                aluno = form.save()
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
            return render(request, "aluno/cadastro_aluno.html", {"form": form})
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

    return render(request, "aluno/cadastro_aluno.html", {"form": form})