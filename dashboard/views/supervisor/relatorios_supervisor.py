from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from dashboard.models import Estagio, RelatorioEstagio


@login_required
@user_passes_test(lambda u: hasattr(u, "supervisor") and u.supervisor)
def relatorios_supervisor(request):
    supervisor = request.user.supervisor
    estagios = Estagio.objects.filter(supervisor=supervisor)
    relatorios_por_estagio = {}

    for estagio in estagios:
        relatorios = RelatorioEstagio.objects.filter(estagio=estagio).order_by("data_prevista")
        relatorios_por_estagio[estagio.id] = {
            "estagio": estagio,
            "relatorios": relatorios
        }

    context = {
        "relatorios_por_estagio": relatorios_por_estagio,
        "supervisor": supervisor,
    }
    return render(request, "supervisor/relatorios_supervisor.html", context)