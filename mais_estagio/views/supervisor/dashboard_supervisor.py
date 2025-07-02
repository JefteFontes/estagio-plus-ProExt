# dashboard/views/supervisor/dashboard_supervisor.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from mais_estagio.models import Estagio


@login_required
@user_passes_test(lambda u: hasattr(u, "supervisor") and u.supervisor)
def dashboard_supervisor(request):
    supervisor = request.user.supervisor
    estagios = Estagio.objects.filter(supervisor=supervisor).select_related("estagiario", "empresa", "orientador")
    context = {
        "supervisor": supervisor,
        "estagios": estagios,
    }
    return render(request, "supervisor/dashboard_supervisor.html", context)