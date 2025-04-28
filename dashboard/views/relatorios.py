from django.shortcuts import render
import datetime
from dateutil.relativedelta import relativedelta
from dashboard.models import Estagio


def relatorios(request):
    estagios = Estagio.objects.all()
    relatorios_por_estagio = {}

    for estagio in estagios:
        relatorios = verificar_relatorios_pendentes(estagio)
        if relatorios:
            # Convertendo datas para string
            for relatorio in relatorios:
                relatorio["data_prevista"] = relatorio["data_prevista"].strftime(
                    "%d/%m/%Y"
                )

            relatorios_por_estagio[estagio.id] = {
                "estagio": estagio,
                "relatorios": relatorios,
            }

    return render(
        request,
        "dashboard_relatorios.html",
        {"relatorios_por_estagio": relatorios_por_estagio},
    )


def verificar_relatorios_pendentes(estagio):
    hoje = datetime.date.today()
    relatorios = []

    if hoje >= estagio.data_inicio:
        relatorios.append(
            {
                "tipo": "Termo de Compromisso",
                "data_prevista": estagio.data_inicio,
                "dias_atraso": (
                    (hoje - estagio.data_inicio).days
                    if hoje > estagio.data_inicio
                    else 0
                ),
            }
        )

    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append(
            {
                "tipo": "Relatório Semestral",
                "data_prevista": data,
                "dias_atraso": (hoje - data).days if hoje > data else 0,
            }
        )
        data += relativedelta(months=6)

    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append(
                {
                    "tipo": tipo,
                    "data_prevista": estagio.data_fim,
                    "dias_atraso": (
                        (hoje - estagio.data_fim).days if hoje > estagio.data_fim else 0
                    ),
                }
            )

    return relatorios


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
        relatorios.append(
            {
                "tipo": "Termo de Compromisso",
                "data_prevista": estagio.data_inicio,
                "dias_atraso": formatar_atraso(estagio.data_inicio),
            }
        )

    data = estagio.data_inicio + relativedelta(months=6)
    while data <= hoje and data < estagio.data_fim:
        relatorios.append(
            {
                "tipo": "Relatório Semestral",
                "data_prevista": data,
                "dias_atraso": formatar_atraso(data),
            }
        )
        data += relativedelta(months=6)

    if hoje >= estagio.data_fim:
        for tipo in ["Relatório de Avaliação", "Relatório de Conclusão"]:
            relatorios.append(
                {
                    "tipo": tipo,
                    "data_prevista": estagio.data_fim,
                    "dias_atraso": formatar_atraso(estagio.data_fim),
                }
            )

    return relatorios
