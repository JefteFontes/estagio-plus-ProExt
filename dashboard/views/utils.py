# dashboard/views/utils.py

import traceback
import requests
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db import transaction
from allauth.account.forms import ResetPasswordForm
# Remova: from pyexpat.errors import messages  <-- ISTO ESTÁ ERRADO E CAUSA PROBLEMAS
from django.contrib import messages # <--- Use esta importação correta para messages

# Importe os módulos nativos do Python para geração de senha aleatória
import secrets
import string

# Obtém o modelo de usuário ativo no seu projeto
User = get_user_model()

# --- Funções de Validação e Busca (Mantidas como estão) ---

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

        return JsonResponse(
            {
                "name": data.get("alias", "")
                or data.get("company", {}).get("name", ""),
                "razao_social": data.get("company", {}).get("name", ""),
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

# --- Função Auxiliar para Geração de Senha Aleatória ---
def gerar_senha_aleatoria(length=12):
    """Gera uma senha aleatória com letras, números e símbolos."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def ativar_acesso_estagiario(request, estagiario_instance):
    if estagiario_instance.user:
        messages.info(request, "Estagiário já possui uma conta de usuário associada.")
        return True, "Estagiário já possui uma conta de usuário associada."

    try:
        with transaction.atomic():
            # 1. Cria o objeto User (sem senha ainda)
            user = User.objects.create_user(
                username=estagiario_instance.email, # O email é usado como username para login
                email=estagiario_instance.email,
                first_name=estagiario_instance.nome_completo.split(' ')[0] if estagiario_instance.nome_completo else '',
                last_name=' '.join(estagiario_instance.nome_completo.split(' ')[1:]) if estagiario_instance.nome_completo else '',
                is_active=True, 
            )

            random_password = gerar_senha_aleatoria(length=16) 
            user.set_password(random_password) 
            user.save() 

            estagiario_instance.user = user
            estagiario_instance.status = True 
            estagiario_instance.save()

            # 4. Envia e-mail de redefinição de senha via django-allauth
            reset_form = ResetPasswordForm({'email': user.email})
            if reset_form.is_valid():
                reset_form.save(request=request) # Isso aciona o envio do email de redefinição
                message = "Usuário criado com sucesso! Um e-mail de redefinição de senha foi enviado para o estagiário."
                return True, message
            else:
                # Se o formulário de redefinição não for válido, loga os erros e informa o problema
                message = "Usuário criado, mas houve um erro ao enviar o e-mail de redefinição de senha. Por favor, contate o suporte."
                print(f"Erro no ResetPasswordForm para {user.email}: {reset_form.errors}")
                return False, message

    except Exception as e:
        # Captura qualquer outro erro inesperado durante o processo
        traceback.print_exc() # Imprime o stack trace completo para depuração
        message = f"Ocorreu um erro inesperado ao ativar o estagiário como usuário: {str(e)}"
        return False, message