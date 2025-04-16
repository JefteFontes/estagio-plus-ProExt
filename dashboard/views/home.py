import os
import tempfile
from django.shortcuts import get_object_or_404, render, redirect
import pdfplumber
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from dashboard.models import (
    Empresa,
    Endereco,
    Estagiario,
    Estagio,
    StatusChoices,
    Supervisor,
    Cursos,
    TipoChoices,
    TurnoChoices,
    CoordenadorExtensao,
    
)
from dashboard.views.utils import parse_sections
from dashboard.forms import CursosCadastroForm, CoordenadorEditForm
from django.db.models import Q


def home(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return render(request, "cadastro/home.html")


def details(request):
    return render(request, "details.html")


def dashboard(request):
    return render(request, "dashboard.html")


def dashboard_cursos(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    instituicao = coordenador.instituicao

    search = request.GET.get("search", "")
    area = request.GET.get("area", "")
    cursos = Cursos.objects.filter(instituicao=instituicao)

    if search:
        cursos = cursos.filter(nome_curso__icontains=search)
    if area:
        cursos = cursos.filter(area=area)

    areas = Cursos.objects.values_list("area", flat=True).distinct()
    context = {
        "cursos": cursos,
        "areas": areas,
    }
    return render(request, "dashboard_cursos.html", context)


def dashboard_empresa(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    instituicao = coordenador.instituicao

    search = request.GET.get("search", "")
    cidade = request.GET.get("cidade", "")
    empresas = Empresa.objects.filter(instituicao=instituicao)

    if search:
        empresas = empresas.filter(empresa_nome__icontains=search) | empresas.filter(
            cnpj__icontains=search
        )
    if cidade:
        empresas = empresas.filter(endereco__cidade__icontains=cidade)

    cidades = Empresa.objects.values_list("endereco__cidade", flat=True).distinct()
    context = {
        "empresas": empresas,
        "cidades": cidades,
    }
    return render(request, "dashboard_empresa.html", context)


def dashboard_estagiario(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    instituicao = coordenador.instituicao

    search = request.GET.get("search", "")
    curso = request.GET.get("curso", "")
    search_matricula = request.GET.get("search-matricula", "")

    estagiarios = Estagiario.objects.filter(instituicao=instituicao)
    if search:
        estagiarios = estagiarios.filter(
            Q(nome_completo__icontains=search) | Q(matricula__icontains=search)
        )
    if curso:
        estagiarios = estagiarios.filter(curso__nome_curso__icontains=curso)
    if search_matricula:
        estagiarios = estagiarios.filter(matricula__startswith=search_matricula)

    cursos = Cursos.objects.values_list("nome_curso", flat=True).distinct()

    context = {
        "estagiarios": estagiarios,
        "cursos": cursos,
    }
    return render(request, "dashboard_estagiario.html", context)


@login_required
def dashboard_instituicao(request):
    errors = []
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    instituicao = coordenador.instituicao

    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.read())
            file_path = temp_file.name

        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

                sections = parse_sections(text)
                print(
                    f"Seções extraídas: {sections.keys()}"
                )  # Log das seções extraídas
            print("- - - - - - - - - - - - - - - - - - - - - -")

            # Tratamento dos dados da empresa
            empresa_data = sections.get("empresa", {})
            if not empresa_data:
                errors.append("Dados da empresa não encontrados no PDF.")
                raise Exception("Erro: Dados da empresa ausentes no PDF.")

            try:
                empresa = Empresa.objects.get(email=empresa_data.get("email", ""))
                print(
                    f"Empresa já existente: {empresa.nome}"
                )  # Log da empresa encontrada
            except Empresa.DoesNotExist:
                endereco_empresa = Endereco.objects.create(
                    rua=empresa_data.get("rua", ""),
                    numero=empresa_data.get("numero", ""),
                    bairro=empresa_data.get("bairro", ""),
                    cidade=empresa_data.get("cidade", ""),
                    estado=empresa_data.get("estado", ""),
                    cep=empresa_data.get("cep", ""),
                )
                empresa = Empresa.objects.create(
                    nome=empresa_data.get("nome", ""),
                    cnpj=empresa_data.get("cnpj", ""),
                    razao_social=empresa_data.get("razao_social", ""),
                    endereco=endereco_empresa,
                    email=empresa_data.get("email", ""),
                )

            # Tratamento dos dados do estagiário
            estagiario_data = sections.get("estagiário", {})
            if not estagiario_data:
                errors.append("Dados do estagiário não encontrados no PDF.")
                raise Exception("Erro: Dados do estagiário ausentes no PDF.")

            endereco_estagiario = Endereco.objects.create(
                rua=estagiario_data.get("rua", ""),
                numero=estagiario_data.get("numero", ""),
                bairro=estagiario_data.get("bairro", ""),
                cidade=estagiario_data.get("cidade", ""),
                estado=estagiario_data.get("estado", ""),
                cep=estagiario_data.get("cep", ""),
            )

            estagiario = Estagiario.objects.create(
                nome_completo=estagiario_data.get("nome_completo", ""),
                cpf=estagiario_data.get("cpf", ""),
                matricula=estagiario_data.get("matricula", ""),
                curso=estagiario_data.get("curso", ""),
                telefone=estagiario_data.get("telefone", ""),
                email=estagiario_data.get("email", ""),
                endereco=endereco_estagiario,  # Associando o endereço ao estagiário
            )

            # Tratamento dos dados do estágio
            estagio_data = sections.get("estágio", {})
            if not estagio_data:
                errors.append("Dados do estágio não encontrados no PDF.")
                raise Exception("Erro: Dados do estágio ausentes no PDF.")

            supervisor = Supervisor.objects.get(nome=estagio_data.get("supervisor", ""))
            Estagio.objects.create(
                bolsa_estagio=estagio_data.get('bolsa', ''),
                area=estagio_data.get('area', ''),
                tipo_estagio=estagio_data.get('tipo_estagio', ''),
                descricao=estagio_data.get('descricao', ''),
                data_inicio=estagio_data.get('data_inicio', None),
                data_fim=estagio_data.get('data_fim', None),
                turno=estagio_data.get('turno', ''),
                estagiario=estagiario,
                empresa=empresa,
                orientador=estagio_data.get('orientador', ''),
                supervisor=supervisor,
            )

        except Exception as e:
            errors.append(f"Erro ao processar o PDF ou salvar dados: {str(e)}")
            print(f"Erro detalhado: {str(e)}")  # Log do erro

        finally:
            os.remove(file_path)

    area = request.GET.get('area', '')
    status = request.GET.get('status', '')
    turno = request.GET.get('turno', '')
    tipo = request.GET.get('tipo_estagio', '')

    estagios = Estagio.objects.filter(instituicao=instituicao)
    if area:
        estagios = estagios.filter(area=area)
    if status:
        estagios = estagios.filter(status=status)
    if turno:
        estagios = estagios.filter(turno=turno)
    if tipo:
        estagios = estagios.filter(tipo_estagio=tipo)

    areas = Estagio.objects.values_list("area", flat=True).distinct()
    status_choices = [choice[0] for choice in StatusChoices.choices]
    turnos = [choice[0] for choice in TurnoChoices.choices]
    tipos = [choice[0] for choice in TipoChoices.choices]

    context = {
        'areas': areas,
        'tipos': tipos,
        'status_choices': status_choices,
        'turnos': turnos,
        'estagios': estagios,
        'estagios_ativos': len(estagios),
        'instituicao': instituicao,
        'errors': errors,
    }
    return render(request, "dashboard_instituicao.html", context)


def cadastrar_cursos(request):
    coordenador_extensao = CoordenadorExtensao.objects.get(user=request.user)

    if request.method == "POST":
        form = CursosCadastroForm(
            coordenador_extensao=coordenador_extensao, data=request.POST
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Curso cadastrado com sucesso!")
            return redirect("dashboard_cursos")
    else:
        form = CursosCadastroForm()

    return render(
        request,
        "cadastrar_cursos.html",
        {"form": form},
    )


def editar_curso(request, curso_id):
    curso = get_object_or_404(Cursos, id=curso_id)

    if request.method == "POST":
        form = CursosCadastroForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect("dashboard_cursos")
    else:
        form = CursosCadastroForm(instance=curso)
    return render(request, 'cadastrar_cursos.html', {'form': form, 'curso': curso})


def deletar_curso(request, curso_id):
    curso = get_object_or_404(Cursos, id=curso_id)
    #mensagem de erro se tiver estagiario vinculado ao curso
    if Estagiario.objects.filter(curso=curso).exists():
        messages.error(request, 'O curso possui estagiarios vinculados e nao pode ser deletado.')
        return redirect('dashboard_cursos')
    else:
        curso.delete()
        messages.success(request, "Curso deletado com sucesso!")
        return redirect(
            "dashboard_cursos"
        )  # Certifique-se que 'dashboard_cursos' seja a URL correta
    # Renderizar uma página de confirmação (opcional)
    return render(request, "dashboard_cursos.html", {"cursos": cursos})


def detalhes_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)
   
    return render(request, 'details.html', {
        'estagio': estagio,
    })

def relatorios(request):
    return render(request, 'dashboard_relatorios.html')
