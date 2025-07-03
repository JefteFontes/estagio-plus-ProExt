from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
from django.shortcuts import render
from mais_estagio.models import (
    Estagio,
    Empresa,
    Supervisor,
    Aluno,
)
from django.utils.dateparse import parse_date



def dashboard_personalizados(request):
    context = {
        "areas": Estagio.objects.values_list("area", flat=True).distinct(),
        "status_choices": Estagio._meta.get_field("status").choices,
        "tipo_choices": Estagio._meta.get_field("tipo_estagio").choices,
        "turnos": Estagio._meta.get_field("turno").choices,
        "empresas": Empresa.objects.all(),
        "supervisores": Supervisor.objects.all(),
        "estagiarios": Estagiario.objects.all()
        
    }
    return render(request, 'dashboard_personalizados.html', context)


def relatorio_personalidizado(request):
    estagios = Estagio.objects.all()

    # Filtros
    area = request.GET.get("area")
    status = request.GET.get("status")
    tipo_estagio = request.GET.get("tipo_estagio")
    turno = request.GET.get("turno")
    empresa = request.GET.get("empresa.empresa_nome")
    supervisor = request.GET.get("supervisor.nome_completo")
    data_inicio_de = parse_date(request.GET.get("data_inicio_de"))
    data_inicio_ate = parse_date(request.GET.get("data_inicio_ate"))
    data_fim_de = parse_date(request.GET.get("data_fim_de"))
    data_fim_ate = parse_date(request.GET.get("data_fim_ate"))

    # Aplicando filtros (só se valores existirem)
    if area:
        estagios = estagios.filter(area=area)
    if status:
        estagios = estagios.filter(status=status)
    if tipo_estagio:
        estagios = estagios.filter(tipo_estagio=tipo_estagio)
    if turno:
        estagios = estagios.filter(turno=turno)
    if empresa:
        estagios = estagios.filter(empresa=empresa)
    if supervisor:
        estagios = estagios.filter(supervisor=supervisor)
    if data_inicio_de and data_inicio_ate:
        estagios = estagios.filter(data_inicio__range=(data_inicio_de, data_inicio_ate))
    if data_fim_de and data_fim_ate:
        estagios = estagios.filter(data_fim__range=(data_fim_de, data_fim_ate))

    context = {
        "estagios": estagios,
        "filtros": request.GET,
        "instituicao": Estagio.objects.first().instituicao
    }
    return render(request, "relatorio_personalizado.html", context)
