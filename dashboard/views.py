import re
import os
import tempfile
import pdfplumber
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EstagiarioCadastroForm


def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def cadastrar_estagiario(request):
    if request.method == 'POST':
        form = EstagiarioCadastroForm(request.POST)
        if form.is_valid():
            form.save(commit=True, coordenador=request.user.coordenadorextensao)
            return redirect('dashboard_instituicao')  # Redireciona para o dashboard após o cadastro
    else:
        form = EstagiarioCadastroForm()
    
    return render(request, 'cadastrar_estagiario.html', {'form': form})


def get_vagas(new_vaga=None):
    vagas = [
        {'nome': 'Nome do Estágio 1', 'empresa': 'Empresa 1', 'data': '11/01/2050', 'status': 'Pendente'},
        {'nome': 'Nome do Estágio 2', 'empresa': 'Empresa 2', 'data': '12/01/2050', 'status': 'Concluído'},
        {'nome': 'Nome do Estágio 3', 'empresa': 'Empresa 3', 'data': '13/01/2050', 'status': 'Pendente'},
        {'nome': 'Nome do Estágio 4', 'empresa': 'Empresa 4', 'data': '14/01/2050', 'status': 'Concluído'},
        {'nome': 'Nome do Estágio 5', 'empresa': 'Empresa 5', 'data': '15/01/2050', 'status': 'Pendente'},
    ]
    if new_vaga:
        vagas.append(new_vaga)
    return vagas


def extract_vaga_from_pdf(file_path):
    vaga = {}
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)

    vaga['nome'] = re.search(r'Curso:\s*(.+)', text).group(1).strip()
    vaga['empresa'] = re.search(r'Razão Social:\s*(.+)', text).group(1).strip()
    vaga['data'] = "01/01/2050"
    vaga['status'] = "Pendente"
    return vaga


@login_required
def dashboard_instituicao(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        # Usar um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())
            file_path = temp_file.name

        # Processar o arquivo PDF
        try:
            new_vaga = extract_vaga_from_pdf(file_path)
            estagios = get_vagas(new_vaga)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        finally:
            # Remover o arquivo temporário após o uso
            os.remove(file_path)
    else:
        estagios = get_vagas()

    context = {
        'estagios': estagios,
        'estagios_ativos': len(estagios),
        'alunos_estagi': 10,

    }

    return render(request, 'dashboard_instituicao.html', context)
