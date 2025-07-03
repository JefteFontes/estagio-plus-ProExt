import os
import tempfile
from django.urls import reverse
import pdfplumber
from django.shortcuts import render, redirect

from home.utils import parse_sections
from ..models import Estagio, Empresa, Supervisor, Endereco

from mais_estagio.models import Aluno


def importar_pdf(request):
    errors = []
    estagio_incompleto_id = None

    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.read())
            file_path = temp_file.name

        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

            sections = parse_sections(text)

            empresa_data = sections.get("empresa", {})
            empresa = Empresa.objects.filter(cnpj=empresa_data.get("cnpj", "")).first()
            if not empresa:
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
            estagiario = Estagiario.objects.filter(
                email=estagiario_data.get("email", "")
            ).first()
            if not estagiario:
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
                    endereco=endereco_estagiario,
                )

            supervisor_data = sections.get("supervisor", {})
            supervisor, created = Supervisor.objects.get_or_create(
                cpf=supervisor_data.get("cpf", ""),
                defaults={
                    "nome_completo": supervisor_data.get("nome_completo", ""),
                    "email": supervisor_data.get("email", ""),
                    "telefone": supervisor_data.get("telefone", ""),
                    "empresa": empresa,
                },
            )

            estagio_data = sections.get("estágio", {})
            estagio = Estagio.objects.create(
                bolsa_estagio=estagio_data.get("bolsa", "") or None,
                area=estagio_data.get("area", "") or None,
                descricao=estagio_data.get("descricao", "") or None,
                data_inicio=estagio_data.get("data_inicio", None),
                data_fim=estagio_data.get("data_fim", None),
                turno=estagio_data.get("turno", "") or None,
                estagiario=estagiario,
                empresa=empresa,
                supervisor=supervisor,
            )

            if not all([estagio.bolsa_estagio, estagio.area, estagio.descricao]):
                estagio_incompleto_id = (
                    estagio.id
                )  

        except Exception as e:
            errors.append(f"Erro ao processar o PDF ou salvar dados: {str(e)}")

        finally:
            os.remove(file_path)

        if estagio_incompleto_id:
            return redirect(
                reverse("complementar_estagio", args=[estagio_incompleto_id])
            )

    return render(
        request,
        "dashboard_instituicao.html",
        {
            "estagios": Estagio.objects.all(),
            "errors": errors,
            "estagios_ativos": len(Estagio.objects.all()),
        },
    )
