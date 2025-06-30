from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from dashboard.models import Estagio, RelatorioEstagio

@login_required
@user_passes_test(lambda u: hasattr(u, "orientador") and u.orientador)
def relatorios_orientador(request):
    orientador = request.user.orientador
    estagios = Estagio.objects.filter(orientador=orientador)
    relatorios_por_estagio = {}

    for estagio in estagios:
        relatorios = RelatorioEstagio.objects.filter(estagio=estagio).order_by("data_prevista")
        relatorios_por_estagio[estagio.id] = {
            "estagio": estagio,
            "relatorios": relatorios
        }

    context = {
        "relatorios_por_estagio": relatorios_por_estagio,
        "orientador": orientador,
    }
    return render(request, "orientador/relatorios_orientador.html", context)