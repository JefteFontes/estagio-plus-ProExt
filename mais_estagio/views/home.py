import os
import tempfile
from django.shortcuts import get_object_or_404, render, redirect
import pdfplumber
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from mais_estagio.models import (
    Empresa,
    Endereco,
    Aluno,
    Estagio,
    StatusChoices,
    Supervisor,
    Cursos,
    TipoChoices,
    TurnoChoices,
    CoordenadorExtensao,
)
from home.utils import parse_sections
from mais_estagio.views.estagios import verificar_pendencias
from mais_estagio.forms import CursosCadastroForm, EmpresaCadastroForm
from django.db.models import Q
from django.http import HttpResponseForbidden


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
    coordenador = request.GET.get("coordenador", "")
    cursos = Cursos.objects.filter(instituicao=instituicao)

    if search:
        cursos = cursos.filter(nome_curso__icontains=search)
    if area:
        cursos = cursos.filter(area=area)
    if coordenador:
        cursos = cursos.filter(coordenador__icontains=coordenador) 

    areas = Cursos.objects.values_list("area", flat=True).distinct()
    context = {
        "cursos": cursos,
        "areas": areas,
        "coordenador": coordenador,
    }
    return render(request, "dashboard_cursos.html", context)


def dashboard_empresa(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    instituicao = coordenador.instituicao

    search = request.GET.get("search", "")
    cidade = request.GET.get("cidade", "")
    empresas = Empresa.objects.filter(instituicao=instituicao)

    if search:
        empresas = empresas.filter(nome__icontains=search) | empresas.filter(
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


@login_required
@user_passes_test(lambda u: hasattr(u, 'coordenadorextensao') and u.coordenadorextensao)
def dashboard_estagiario(request):
    try:
        coordenador = CoordenadorExtensao.objects.get(user=request.user)
        instituicao = coordenador.instituicao
    except CoordenadorExtensao.DoesNotExist:
        messages.error(request, "Você não está associado a nenhuma instituição como coordenador.")
        return redirect('alguma_pagina_de_erro_ou_dashboard_padrao') 

    search_query = request.GET.get("search", "")
    search_matricula = request.GET.get("search-matricula", "")
    curso_filter = request.GET.get("curso", "")

    estagiarios_da_instituicao = Aluno.objects.filter(instituicao=instituicao)

    if search_query:
        estagiarios_da_instituicao = estagiarios_da_instituicao.filter(
            Q(nome_completo__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(cpf__icontains=search_query)
        )
    if curso_filter:
        estagiarios_da_instituicao = estagiarios_da_instituicao.filter(
            curso__nome_curso__icontains=curso_filter
        )
    if search_matricula:
        estagiarios_da_instituicao = estagiarios_da_instituicao.filter(
            matricula__startswith=search_matricula
        )

    alunos_cadastrados = estagiarios_da_instituicao.filter(status=True).order_by('nome_completo')
    alunos_aguardando_confirmacao = estagiarios_da_instituicao.filter(status=False).order_by('nome_completo')

    total_estagiarios = alunos_cadastrados.count() + alunos_aguardando_confirmacao.count()
    cursos_disponiveis = Cursos.objects.filter(instituicao=instituicao).order_by('nome_curso')

    context = {
        "alunos_cadastrados": alunos_cadastrados,
        "alunos_aguardando_confirmacao": alunos_aguardando_confirmacao,
        "cursos": cursos_disponiveis, 
        "search_query": search_query, 
        "search_matricula": search_matricula, 
        "curso_filter": curso_filter, 
        "total_estagiarios": total_estagiarios
    }
    return render(request, "dashboard_estagiario.html", context)


@login_required
def dashboard_instituicao(request):
    errors = []

    if hasattr(request.user, "coordenadorextensao") and request.user.coordenadorextensao:
        coordenador = request.user.coordenadorextensao
        instituicao = coordenador.instituicao
        estagios = Estagio.objects.filter(instituicao=instituicao)
    elif hasattr(request.user, 'estagiario'):
        estagiario = request.user.estagiario
        estagios = Estagio.objects.filter(estagiario=estagiario)
        instituicao = estagiario.instituicao if hasattr(estagiario, 'instituicao') else None
    else:
        return HttpResponseForbidden("Acesso não autorizado. Esta página é exclusiva para Coordenadores de Extensão.")

    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.read())
            file_path = temp_file.name

        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

                sections = parse_sections(text)
                print(f"Seções extraídas: {sections.keys()}")
            print("- - - - - - - - - - - - - - - - - - - - - -")

            empresa_data = sections.get("empresa", {})
            if not empresa_data:
                errors.append("Dados da empresa não encontrados no PDF.")
                raise Exception("Erro: Dados da empresa ausentes no PDF.")

            try:
                empresa = Empresa.objects.get(email=empresa_data.get("email", ""))
                print(f"Empresa já existente: {empresa.nome}")
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

            estagiario = Aluno.objects.create(
                nome_completo=estagiario_data.get("nome_completo", ""),
                cpf=estagiario_data.get("cpf", ""),
                matricula=estagiario_data.get("matricula", ""),
                curso=estagiario_data.get("curso", ""),
                telefone=estagiario_data.get("telefone", ""),
                email=estagiario_data.get("email", ""),
                endereco=endereco_estagiario,
            )

            estagio_data = sections.get("estágio", {})
            if not estagio_data:
                errors.append("Dados do estágio não encontrados no PDF.")
                raise Exception("Erro: Dados do estágio ausentes no PDF.")

            supervisor = Supervisor.objects.get(nome=estagio_data.get("supervisor", ""))
            Estagio.objects.create(
                bolsa_estagio=estagio_data.get("bolsa", ""),
                area=estagio_data.get("area", ""),
                tipo_estagio=estagio_data.get("tipo_estagio", ""),
                descricao=estagio_data.get("descricao", ""),
                data_inicio=estagio_data.get("data_inicio", None),
                data_fim=estagio_data.get("data_fim", None),
                turno=estagio_data.get("turno", ""),
                estagiario=estagiario,
                empresa=empresa,
                orientador=estagio_data.get("orientador", ""),
                supervisor=supervisor,
            )

        except Exception as e:
            errors.append(f"Erro ao processar o PDF ou salvar dados: {str(e)}")
            print(f"Erro detalhado: {str(e)}")

        finally:
            os.remove(file_path)

    area = request.GET.get("area", "")
    status = request.GET.get("status", "")
    turno = request.GET.get("turno", "")
    tipo = request.GET.get("tipo_estagio", "")
    estagios_num = Estagio.objects.filter(instituicao=instituicao).count()

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
        "areas": areas,
        "tipos": tipos,
        "status_choices": status_choices,
        "turnos": turnos,
        "estagios": estagios,
        "estagios_ativos": estagios_num,
        "instituicao": instituicao,
        "errors": errors,
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
    return render(request, "cadastrar_cursos.html", {"form": form, "curso": curso})


def deletar_curso(request, curso_id):
    curso = get_object_or_404(Cursos, id=curso_id)
    # mensagem de erro se tiver aluno vinculado ao curso
    if Aluno.objects.filter(curso=curso).exists():
        messages.error(
            request, "O curso possui estagiarios vinculados e nao pode ser deletado."
        )
        return redirect("dashboard_cursos")
    else:
        curso.delete()
        messages.success(request, "Curso deletado com sucesso!")
        return redirect(
            "dashboard_cursos"
        )  
    return render(request, "dashboard_cursos.html", {"cursos": cursos})


def detalhes_estagio(request, estagio_id):
    estagio = get_object_or_404(Estagio, id=estagio_id)

    return render(
        request,
        "details.html",
        {
            "estagio": estagio,
        },
    )


def relatorios(request):
    return render(request, "dashboard_relatorios.html")
    
