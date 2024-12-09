import re
import os
import tempfile
import pdfplumber
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from . import models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EstagiarioCadastroForm, EmpresaCadastroForm

def home(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'cadastro/home.html')

def details(request):
    return render(request, 'details.html')

@login_required
def cadastrar_estagiario(request):
    if request.method == 'POST':
        form = EstagiarioCadastroForm(request.POST)
        if form.is_valid():
            user, estagiario = form.save()
            return redirect('dashboard_instituicao')  # Redireciona para o dashboard após o cadastro
    else:
        form = EstagiarioCadastroForm()

    return render(request, 'cadastrar_estagiario.html', {'form': form})

@login_required
def cadastrar_empresa(request):
    if request.method == 'POST':
        form = EmpresaCadastroForm(request.POST)
        if form.is_valid():
            user, supervisor = form.save()
            return redirect('dashboard_instituicao')  # Redireciona para a página de login após o cadastro
    else:
        form = EmpresaCadastroForm()
    return render(request, 'cadastrar_empresa.html', {'form': form})

def get_estagio(new_estagio=None):
    estagios = models.Estagio.objects

    if new_estagio:
        estagios = estagios.filter(id=new_estagio.get('id', 0))

    return estagios

def detalhes_vaga(request):
    nome_vaga = request.GET.get('nome', None)
    vagas = get_estagio() 
    vaga = next((v for v in vagas if v["nome"] == nome_vaga), None)
    return render(request, 'details.html', {"vaga": vaga}) 

def extract_estagio_from_pdf(file_path):
    estagio = {}
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)

    estagio['nome'] = re.search(r'Curso:\s*(.+)', text).group(1).strip()
    estagio['empresa'] = re.search(r'Razão Social:\s*(.+)', text).group(1).strip()
    estagio['data'] = "01/01/2050"
    estagio['status'] = "Pendente"
    return estagio


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
            new_estagio = extract_estagio_from_pdf(file_path)
            estagios = get_estagio(new_estagio)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        finally:
            # Remover o arquivo temporário após o uso
            os.remove(file_path)
    else:
        estagios = models.Estagio.objects.all()  # Aqui você faz uma consulta para obter os Estágios

    context = {
        'estagios': estagios,
        'estagios_ativos': len(estagios),
        'alunos_estagi': 10,  # Ajuste conforme a lógica
    }

    return render(request, 'dashboard_instituicao.html', context)
