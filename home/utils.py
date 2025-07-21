import traceback
import os
from docx import Document
import docxedit
from docx2pdf import convert
from num2words import num2words
import requests
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from allauth.account.forms import ResetPasswordForm

from django.contrib import messages  

import secrets
import string
import pythoncom

User = get_user_model()


def parse_sections(text):
    sections = {}
    current_section = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"):
            current_section = line.strip("# ").lower()
            sections[current_section] = {}
        elif current_section:
            key_value = line.split(":", 1)
            if len(key_value) == 2:
                key, value = key_value
                sections[current_section][key.strip().lower()] = value.strip()
    return sections


def buscar_cep(request):
    cep = request.GET.get("cep", "").replace("-", "")

    if len(cep) != 8 or not cep.isdigit():
        return JsonResponse({"error": "CEP inválido"}, status=400)

    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if response.status_code == 200:
        data = response.json()
        if "erro" in data:
            return JsonResponse({"error": "CEP não encontrado"}, status=404)

        return JsonResponse(
            {
                "logradouro": data.get("logradouro", ""),
                "bairro": data.get("bairro", ""),
                "cidade": data.get("localidade", ""),
                "estado": data.get("uf", ""),
            }
        )
    return JsonResponse({"error": "Erro ao buscar CEP"}, status=500)


def validate_cnpj(request):
    cnpj = request.GET.get("cnpj", "")

    if len(cnpj) != 14 or not cnpj.isdigit():
        return JsonResponse({"error": "CNPJ inválido"}, status=400)

    response = requests.get(f"https://open.cnpja.com/office/{cnpj}")
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            return JsonResponse({"error": "CNPJ não encontrado"}, status=404)
        emails = data.get("emails", [])
        email = emails[0].get("address", "") if emails and isinstance(emails, list) and len(emails) > 0 else ""

        phones = data.get("phones", [])
        phone_number = ""
        if phones and isinstance(phones, list) and len(phones) > 0:
            first_phone = phones[0]
            phone_number = f"({first_phone.get('area', '')}) {first_phone.get('number', '')}"
        return JsonResponse(
            {
                "name": data.get("alias", "")
                or data.get("company", {}).get("name", ""),
                "razao_social": data.get("company", {}).get("name", ""),
                "email": email,
                "telefone": phone_number,
                "cep": data.get("address", {}).get("zip", ""),
                "numero": data.get("address", {}).get("number", ""),
                "atividades": data.get("mainActivity", {}).get("text", ""),
                "complemento": data.get("address", {}).get("details", ""),
                "bairro": data.get("address", {}).get("district", ""),
                "cidade": data.get("address", {}).get("city", ""),
                "estado": data.get("address", {}).get("state", ""),
                "rua": data.get("address", {}).get("street", ""),
            }
        )
    return JsonResponse({"error": "Erro ao buscar CNPJ"}, status=500)


def validate_cpf(cpf: str) -> bool:
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    check_digit1 = (sum1 * 10 % 11) % 10

    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    check_digit2 = (sum2 * 10 % 11) % 10

    return check_digit1 == int(cpf[9]) and check_digit2 == int(cpf[10])


def gerar_senha_aleatoria(length=12):
    """Gera uma senha aleatória com letras, números e símbolos."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for i in range(length))
    return password


def ativar_acesso_estagiario(request, estagiario_instance):
    if estagiario_instance.user:
        messages.info(request, "Estagiário já possui uma conta de usuário associada.")
        return True, "Estagiário já possui uma conta de usuário associada."

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=estagiario_instance.email, 
                email=estagiario_instance.email,
                first_name=(
                    estagiario_instance.nome_completo.split(" ")[0]
                    if estagiario_instance.nome_completo
                    else ""
                ),
                last_name=(
                    " ".join(estagiario_instance.nome_completo.split(" ")[1:])
                    if estagiario_instance.nome_completo
                    else ""
                ),
                is_active=True,
            )

            random_password = gerar_senha_aleatoria(length=16)
            user.set_password(random_password)
            user.save()

            estagiario_instance.user = user
            estagiario_instance.status = True
            estagiario_instance.save()

            # 4. Envia e-mail de redefinição de senha via django-allauth
            reset_form = ResetPasswordForm({"email": user.email})
            if reset_form.is_valid():
                reset_form.save(
                    request=request
                )  # Isso aciona o envio do email de redefinição
                message = "Usuário criado com sucesso! Um e-mail de redefinição de senha foi enviado para o estagiário."
                return True, message
            else:
                # Se o formulário de redefinição não for válido, loga os erros e informa o problema
                message = "Usuário criado, mas houve um erro ao enviar o e-mail de redefinição de senha. Por favor, contate o suporte."
                print(
                    f"Erro no ResetPasswordForm para {user.email}: {reset_form.errors}"
                )
                return False, message

    except Exception as e:
        # Captura qualquer outro erro inesperado durante o processo
        traceback.print_exc()  # Imprime o stack trace completo para depuração
        message = (
            f"Ocorreu um erro inesperado ao ativar o estagiário como usuário: {str(e)}"
        )
        return False, message


def preencher_tceu(estagio, template_path):
    safe_student_name = "".join(
        [c for c in estagio.estagiario.nome_completo if c.isalpha() or c.isdigit() or c == " "] 
    ).rstrip()
    base_filename = f'TCE_{safe_student_name.replace(" ", "_")}'

    output_dir = os.path.join(settings.MEDIA_ROOT, "temp_docs")
    os.makedirs(output_dir, exist_ok=True)

    docx_path = os.path.join(output_dir, f"{base_filename}.docx")
    pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")

    try:
        pythoncom.CoInitialize()

        document = Document(template_path)
        estagiario = estagio.estagiario
        empresa = estagio.empresa
        supervisor = estagio.supervisor
        orientador = estagio.orientador
        endereco_estagiario = estagiario.endereco
        endereco_empresa = empresa.endereco

        docxedit.replace_string(
            document, old_string="NomeEstagiario", new_string=estagiario.nome_completo
        )
        docxedit.replace_string(
            document, old_string="MatriculaEstagiario", new_string=estagiario.matricula
        )
        docxedit.replace_string(
            document, old_string="IdEstagiario", new_string=estagiario.cpf
        )
        docxedit.replace_string(
            document, old_string="OrgaoEstagiario", new_string="SSP"
        )
        docxedit.replace_string(
            document, old_string="DataEstagiario", new_string=estagiario.data_nascimento.strftime("%d/%m/%Y")
        )
        docxedit.replace_string(
            document, old_string="CPFEstagiario", new_string=estagiario.cpf
        )
        docxedit.replace_string(
            document, old_string="NaturalidadeEstagiario", new_string="Brasileiro(a)"
        )
        if estagiario.sexo == "M":
            docxedit.replace_string(
                document, old_string="MascEstagiario", new_string="X"
            )
            docxedit.replace_string(
                document, old_string="FemEstagiario", new_string=""
            )
        elif estagiario.sexo == "F":
            docxedit.replace_string(
                document, old_string="FemEstagiario", new_string="X"
            )
            docxedit.replace_string(
                document, old_string="MascEstagiario", new_string=""
            )
        docxedit.replace_string(
            document,
            old_string="CursoEstagiario",
            new_string=estagiario.curso.nome_curso,
        )
        docxedit.replace_string(
            document, old_string="PeriodoEstagiario", new_string=str(estagiario.periodo)
        )
        docxedit.replace_string(
            document, old_string="EmailEstagiario", new_string=estagiario.email
        )
        docxedit.replace_string(
            document, old_string="TelefoneEstagiario", new_string=estagiario.telefone
        )
        docxedit.replace_string(
            document,
            old_string="EnderecoEstagiario",
            new_string=endereco_estagiario.rua,
        )
        docxedit.replace_string(
            document, old_string="NumCasa", new_string=endereco_estagiario.numero
        )
        docxedit.replace_string(
            document,
            old_string="BairroEstagiario",
            new_string=endereco_estagiario.bairro,
        )
        docxedit.replace_string(
            document,
            old_string="EstagiCi",
            new_string=endereco_estagiario.cidade,
        )
        docxedit.replace_string(
            document, old_string="EstagiCeP", new_string=endereco_estagiario.cep
        )
        docxedit.replace_string(
            document, old_string="UFEstagiario", new_string=endereco_estagiario.estado
        )
        docxedit.replace_string(
            document, old_string="EstadoEstagiario", new_string=endereco_estagiario.estado
        )

        docxedit.replace_string(
            document, old_string="RazaoEmpresa", new_string=empresa.nome
        )
        docxedit.replace_string(
            document, old_string="RamoEmpresa", new_string=empresa.atividades
        )
        docxedit.replace_string(
            document, old_string="CNPJEmpresa", new_string=empresa.cnpj
        )
        docxedit.replace_string(
            document,
            old_string="RepresentanteEmpresa",
            new_string=supervisor.nome_completo,
        )
        docxedit.replace_string(
            document, old_string="CPFEmpresaRepresentante", new_string=supervisor.cpf
        )
        docxedit.replace_string(
            document,
            old_string="CargoEmpresaRepresentante",
            new_string=supervisor.cargo,
        )
        docxedit.replace_string(
            document, old_string="EnderecoEmpresa", new_string=endereco_empresa.rua
        )
        docxedit.replace_string(
            document,
            old_string="NEmpresa",
            new_string=endereco_empresa.numero,
        )
        docxedit.replace_string(
            document, old_string="BairroEmpresa", new_string=endereco_empresa.bairro
        )
        docxedit.replace_string(
            document,
            old_string="CidadeEmpresa",
            new_string=endereco_empresa.cidade,
        )
        docxedit.replace_string(
            document, old_string="CEPEmpresa", new_string=endereco_empresa.cep
        )
        docxedit.replace_string(
            document,
            old_string="UFEmpresa",
            new_string=endereco_empresa.estado,
        )
        docxedit.replace_string(
            document, old_string="TelefoneEmpresa", new_string="" 
        )
        docxedit.replace_string(
            document, old_string="EmailEmpresa", new_string="" if not empresa.email else empresa.email
        )

        if supervisor:
            docxedit.replace_string(
                document,
                old_string="EstagiarioSupervisor",
                new_string=supervisor.nome_completo,
            )
            docxedit.replace_string(
                document, old_string="RepresentanteEmpresa", new_string=supervisor.nome_completo
            )
            docxedit.replace_string(
                document, old_string="TelefoneSupervisor", new_string="" if not supervisor.telefone else supervisor.telefone
            )
            docxedit.replace_string(
                document, old_string="CPFEmpresaRepresentante", new_string="" if not supervisor.cpf else supervisor.cpf
            )
            docxedit.replace_string(
                document, old_string="CPFSupervisor", new_string="" if not supervisor.cpf else supervisor.cpf
            )
            docxedit.replace_string(
                document,
                old_string="CargoEmpresaRepresentante",
                new_string=supervisor.cargo,
            )
            docxedit.replace_string(document, old_string="EmailSupervisor", new_string=supervisor.email)
            docxedit.replace_string(
                document,
                old_string="Nome do Supervisor/Preceptor:",
                new_string=f"Nome do Supervisor/Preceptor: {supervisor.nome_completo}",
            )

        
        if orientador:
            docxedit.replace_string(document, old_string="ProfessorOrientador", new_string=orientador.nome_completo)

        docxedit.replace_string(
            document,
            old_string="Início: __/__/___",
            new_string=f"Início: {estagio.data_inicio.strftime('%d/%m/%Y')}",
        )
        docxedit.replace_string(
            document,
            old_string="Término: ___/___/___",
            new_string=f"Término: {estagio.data_fim.strftime('%d/%m/%Y')}",
        )

        docxedit.replace_string(
            document,
            old_string="CgSem",
            new_string=f"{estagio.carga_horaria} horas",
        )

        bolsa_valor = estagio.bolsa_estagio or 0
        bolsa_extenso = num2words(bolsa_valor, lang="pt_BR", to="currency")
        docxedit.replace_string(
            document,
            old_string="R$___ (___)",
            new_string=f"R${bolsa_valor:.2f} ({bolsa_extenso})",
        )

        auxilio_valor = estagio.auxilio_transporte or 0
        auxilio_extenso = num2words(auxilio_valor, lang="pt_BR", to="currency")
        docxedit.replace_string(
            document,
            old_string="R$___ (__)",
            new_string=f"R${auxilio_valor:.2f} ({auxilio_extenso})",
        )
        docxedit.replace_string(document, old_string="_/_/_ a _/_/_ ", new_string=f"{estagio.data_inicio.strftime('%d/%m/%Y')} a {estagio.data_fim.strftime('%d/%m/%Y')}")

        docxedit.replace_string(
            document,
            old_string="AtividadesEstag",
            new_string=estagio.descricao or "Atividades não especificadas",
        )

        safe_student_name = "".join(
            [c for c in estagiario.nome_completo if c.isalpha() or c.isdigit() or c == " "]
        ).rstrip()
        output_filename = f'TCE_{safe_student_name.replace(" ", "_")}.docx'
        output_path = os.path.join(settings.MEDIA_ROOT, "temp_docs", output_filename)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        document.save(docx_path)

        convert(docx_path, pdf_path)

        return pdf_path

    except Exception as e:
        print(f"Ocorreu um erro ao gerar o documento: {e}")
        return None
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)

        pythoncom.CoUninitialize()
