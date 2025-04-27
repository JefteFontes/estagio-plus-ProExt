import os
import re
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import datetime
from dateutil.relativedelta import relativedelta
import fitz
from dashboard.models import Estagio
from django.core.files.base import File
import datetime

def relatorios(request):
    estagios = Estagio.objects.all()
    relatorios_por_estagio = {}

    for estagio in estagios:
        relatorios = verificar_relatorios_pendentes(estagio)
        if relatorios:
            # Convertendo datas para string
            for relatorio in relatorios:
                relatorio["data_prevista"] = relatorio["data_prevista"].strftime("%d/%m/%Y")

            relatorios_por_estagio[estagio.id] = {
                "estagio": estagio,
                "relatorios": relatorios
            }

    return render(request, "dashboard_relatorios.html", {
        "relatorios_por_estagio": relatorios_por_estagio
    })


def verificar_relatorios_pendentes(estagio):
    hoje = datetime.date.today()
    relatorios = []

    def formatar_atraso(data_prevista):
        if hoje <= data_prevista:
            return "No prazo"
        diff = relativedelta(hoje, data_prevista)
        partes = []
        if diff.years:
            partes.append(f"{diff.years} ano{'s' if diff.years > 1 else ''}")
        if diff.months:
            partes.append(f"{diff.months} mes{'es' if diff.months > 1 else ''}")
        if diff.days:
            partes.append(f"{diff.days} dia{'s' if diff.days > 1 else ''}")
        return f"{' e '.join(partes)} de atraso"

    if hoje >= estagio.data_inicio:
        relatorios.append({
            "tipo": "Termo de Compromisso",
            "data_prevista": estagio.data_inicio,
            "dias_atraso": formatar_atraso(estagio.data_inicio)
        })

    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append({
            "tipo": "Relatório Semestral",
            "data_prevista": data,
            "dias_atraso": formatar_atraso(data)
        })
        data += relativedelta(months=6)

    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append({
                "tipo": tipo,
                "data_prevista": estagio.data_fim,
                "dias_atraso": formatar_atraso(estagio.data_fim)
            })

    return relatorios


def importar_termo(request, estagio_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'})

    arquivo = request.FILES.get('termo')
    if not arquivo:
        return JsonResponse({'success': False, 'message': 'Nenhum arquivo enviado.'})

    # Pasta temporária
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temporarios')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, 'temp_importar_termo.pdf')

    with open(temp_path, 'wb+') as destination:
        for chunk in arquivo.chunks():
            destination.write(chunk)

    # Ler o PDF
    texto = ""
    with fitz.open(temp_path) as doc:
        for page in doc:
            texto += page.get_text()

    # Buscar informações
    cpf_match = re.search(r'CPF.*?(\d{3}\.?\d{3}\.?\d{3}-?\d{2})', texto)
    cnpj_match = re.search(r'Empresa Concedente.*?CNPJ.*?(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})', texto)
    data_inicio_match = re.search(r'in[ií]cio.*?(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)

    if not (cpf_match and cnpj_match and data_inicio_match):
        return JsonResponse({'success': False, 'message': 'Informações (CPF, CNPJ ou Data de Início) não encontradas no PDF.'})

    cpf_extraido = cpf_match.group(1).replace('-', '').strip()
    cnpj_extraido = cnpj_match.group(1).strip()
    data_inicio_extraida = datetime.datetime.strptime(data_inicio_match.group(1), "%d/%m/%Y").date()

    estagio = Estagio.objects.get(id=estagio_id)
    estagiario_atual = estagio.estagiario.cpf
    empresa_atual = estagio.empresa.cnpj
    data_inicio_atual = estagio.data_inicio

    # Validações
    erros = []
    if cpf_extraido != estagiario_atual:
        erros.append(
            f"CPF do arquivo ({cpf_extraido}) diferente do CPF do estagiário ({estagiario_atual})."
        )
    if cnpj_extraido != empresa_atual:
        erros.append(
            f"CNPJ do arquivo ({cnpj_extraido}) diferente do CNPJ da empresa ({empresa_atual})."
        )
    if data_inicio_extraida != data_inicio_atual:
        erros.append(
            f"Data de início do arquivo ({data_inicio_extraida}) diferente da data de início do estágio ({data_inicio_atual})."
        )

    if erros:
        return JsonResponse({'success': False, 'message': '<br>'.join(erros)})

    # Se passou em todas as validações, salva o arquivo
    ano = estagio.data_inicio.year
    nome_estagiario = estagio.estagiario.nome_completo.replace(' ', '').lower()
    nome_arquivo = f"{ano}TCE_{nome_estagiario}.pdf"

    with open(temp_path, 'rb') as f:
        estagio.pdf_termo.save(nome_arquivo, File(f), save=True)

    return JsonResponse({'success': True, 'message': 'Termo importado com sucesso!', 'url_pdf': estagio.pdf_termo.url})
