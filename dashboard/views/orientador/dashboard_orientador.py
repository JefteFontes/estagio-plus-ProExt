from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from dashboard.models import Estagio, RelatorioEstagio


@login_required
@user_passes_test(lambda u: hasattr(u, "orientador") and u.orientador)
def dashboard_orientador(request):
    orientador = request.user.orientador
    estagios = Estagio.objects.filter(orientador=orientador).select_related("estagiario", "empresa", "supervisor")
    # Busca os relatórios de cada estágio usando o related_name padrão do Django
    relatorios_por_estagio = {
        estagio.id: RelatorioEstagio.objects.filter(estagio=estagio).order_by("data_prevista")
        for estagio in estagios
    }
    context = {
        "orientador": orientador,
        "estagios": estagios,
        "relatorios_por_estagio": relatorios_por_estagio,
    }
    return render(request, "orientador/dashboard_orientador.html", context)