from django.db.models import Q
from dashboard.models import Estagio, CoordenadorExtensao
import datetime
from dateutil.relativedelta import relativedelta
from dashboard.views.estagios import verificar_relatorios_pendentes

def relatorios_pendentes(request):
    if not request.user.is_authenticated:
        return {'relatorios_pendentes_count': 0, 'relatorios_resumo': ''}
    
    try:
        coordenador = CoordenadorExtensao.objects.get(user=request.user)
        instituicao = coordenador.instituicao
        estagios = Estagio.objects.filter(instituicao=instituicao).select_related('estagiario__curso')
        
        count = 0
        hoje = datetime.date.today()
        resumo = []
        
        for estagio in estagios:
            relatorios = verificar_relatorios_pendentes(estagio)
            if relatorios:
                count += len(relatorios)
                curso = estagio.estagiario.curso.nome_curso if estagio.estagiario.curso else 'Curso não informado'
                resumo.append(f"{estagio.estagiario.nome_completo} ({curso}):")
                
                for relatorio in relatorios:
                    dias_atraso = (hoje - relatorio['data_prevista']).days
                    status = f"(Atrasado há {dias_atraso} dias)" if dias_atraso > 0 else "(A vencer)"
                    resumo.append(
                        f"  {relatorio['tipo']}: {relatorio['data_prevista'].strftime('%d/%m/%Y')} {status}"
                    )
        
        return {
            'relatorios_pendentes_count': count,
            'relatorios_resumo': '\n'.join(resumo) if resumo else 'Nenhum relatório pendente'
        }
    
    except CoordenadorExtensao.DoesNotExist:
        return {'relatorios_pendentes_count': 0, 'relatorios_resumo': ''}