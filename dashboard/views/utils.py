from django.http import JsonResponse
import requests

def parse_sections(text):
    sections = {}
    current_section = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Identifica uma nova seção
        if line.startswith('#'):
            current_section = line.strip('# ').lower()
            sections[current_section] = {}
        elif current_section:
            # Divide cada linha da seção em chave e valor
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                sections[current_section][key.strip().lower()] = value.strip()

    return sections

def buscar_cep(request):
    cep = request.GET.get('cep', '').replace('-', '')

    if len(cep) != 8 or not cep.isdigit():
        return JsonResponse({'error': 'CEP inválido'}, status=400)

    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    if response.status_code == 200:
        data = response.json()
        if 'erro' in data:
            return JsonResponse({'error': 'CEP não encontrado'}, status=404)

        return JsonResponse({
            'logradouro': data.get('logradouro', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('localidade', ''),
            'estado': data.get('uf', '')
        })

    return JsonResponse({'error': 'Erro ao buscar CEP'}, status=500)

