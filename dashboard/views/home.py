import os
import tempfile
from django.shortcuts import render, redirect
import pdfplumber
from django.contrib.auth.decorators import login_required
from dashboard.models import Empresa, Endereco, Estagiario, Estagio, Supervisor, Cursos
from dashboard.views.utils import parse_sections
from dashboard.forms import CursosCadastroForm
def home(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    return render(request, 'cadastro/home.html')

def details(request):
    return render(request, 'details.html')

def dashboard(request):
    return render(request, 'dashboard.html')
def dashboard_cursos(request):
    cursos = Cursos.objects.all()
    context = { 'cursos': cursos}
    return render(request, 'dashboard_cursos.html', context)
def dashboard_empresa(request):
    empresas = Empresa.objects.all()
    context = { 'empresas': empresas}
    return render(request, 'dashboard_empresa.html', context)
def dashboard_estagiario(request):
    estagiarios = Estagiario.objects.all()
    context = { 'estagiarios': estagiarios}
    return render(request, 'dashboard_estagiario.html', context)
@login_required
def dashboard_instituicao(request):
    errors = []
    estagios = Estagio.objects.all()

    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.read())
            file_path = temp_file.name

        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or '' for page in pdf.pages)

                sections = parse_sections(text)
                print(f"Seções extraídas: {sections.keys()}")  # Log das seções extraídas
            print("- - - - - - - - - - - - - - - - - - - - - -")

            # Tratamento dos dados da empresa
            empresa_data = sections.get('empresa', {})
            if not empresa_data:
                errors.append("Dados da empresa não encontrados no PDF.")
                raise Exception("Erro: Dados da empresa ausentes no PDF.")

            try:
                empresa = Empresa.objects.get(email=empresa_data.get('email', ''))
                print(f"Empresa já existente: {empresa.nome}")  # Log da empresa encontrada
            except Empresa.DoesNotExist:
                endereco_empresa = Endereco.objects.create(
                    rua=empresa_data.get('rua', ''),
                    numero=empresa_data.get('numero', ''),
                    bairro=empresa_data.get('bairro', ''),
                    cidade=empresa_data.get('cidade', ''),
                    estado=empresa_data.get('estado', ''),
                    cep=empresa_data.get('cep', ''),
                )
                empresa = Empresa.objects.create(
                    nome=empresa_data.get('nome', ''),
                    cnpj=empresa_data.get('cnpj', ''),
                    razao_social=empresa_data.get('razao_social', ''),
                    endereco=endereco_empresa,
                    email=empresa_data.get('email', ''),
                )

            # Tratamento dos dados do estagiário
            estagiario_data = sections.get('estagiário', {})
            if not estagiario_data:
                errors.append("Dados do estagiário não encontrados no PDF.")
                raise Exception("Erro: Dados do estagiário ausentes no PDF.")

            endereco_estagiario = Endereco.objects.create(
                rua=estagiario_data.get('rua', ''),
                numero=estagiario_data.get('numero', ''),
                bairro=estagiario_data.get('bairro', ''),
                cidade=estagiario_data.get('cidade', ''),
                estado=estagiario_data.get('estado', ''),
                cep=estagiario_data.get('cep', ''),
            )

            estagiario = Estagiario.objects.create(
                primeiro_nome=estagiario_data.get('primeiro_nome', ''),
                sobrenome=estagiario_data.get('sobrenome', ''),
                cpf=estagiario_data.get('cpf', ''),
                matricula=estagiario_data.get('matricula', ''),
                curso=estagiario_data.get('curso', ''),
                telefone=estagiario_data.get('telefone', ''),
                email=estagiario_data.get('email', ''),
                endereco=endereco_estagiario,  # Associando o endereço ao estagiário
            )

            # Tratamento dos dados do estágio
            estagio_data = sections.get('estágio', {})
            if not estagio_data:
                errors.append("Dados do estágio não encontrados no PDF.")
                raise Exception("Erro: Dados do estágio ausentes no PDF.")

            supervisor = Supervisor.objects.get(nome=estagio_data.get('supervisor', ''))
            Estagio.objects.create(
                bolsa_estagio=estagio_data.get('bolsa', ''),
                area=estagio_data.get('area', ''),
                descricao=estagio_data.get('descricao', ''),
                data_inicio=estagio_data.get('data_inicio', None),
                data_fim=estagio_data.get('data_fim', None),
                turno=estagio_data.get('turno', ''),
                estagiario=estagiario,
                empresa=empresa,
                supervisor=supervisor,
            )

        except Exception as e:
            errors.append(f"Erro ao processar o PDF ou salvar dados: {str(e)}")
            print(f"Erro detalhado: {str(e)}")  # Log do erro

        finally:
            os.remove(file_path)

    context = {
        'estagios': estagios,
        'estagios_ativos': len(estagios),
        'instituicao': estagios.first().instituicao if estagios.exists() else None,
        'errors': errors,
    }
    return render(request, 'dashboard_instituicao.html', context)

def cadastrar_cursos(request):
    if request.method == 'POST':
        form = CursosCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_cursos')
    else:
        form = CursosCadastroForm()

    return render(request, 'cadastrar_cursos.html', {'form': form}, )
