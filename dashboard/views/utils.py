from django.http import JsonResponse
import requests


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
            # Divide cada linha da seção em chave e valor
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

