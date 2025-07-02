from django.db.models import Q
from mais_estagio.models import Estagio, CoordenadorExtensao
import datetime
from dateutil.relativedelta import relativedelta
from mais_estagio.views.estagios import verificar_relatorios_pendentes

def relatorios_pendentes(request):
    if not request.user.is_authenticated:
        return {
            'relatorios_pendentes_count': 0,
            'relatorios_list': [],
            'relatorios_resumo': ''
        }
    
    try:
        coordenador = CoordenadorExtensao.objects.get(user=request.user)
        instituicao = coordenador.instituicao
        estagios = Estagio.objects.filter(instituicao=instituicao).select_related('estagiario__curso')
        
        count = 0
        hoje = datetime.date.today()
        relatorios_list = []
        resumo_lines = []
        
        for estagio in estagios:
            relatorios = verificar_relatorios_pendentes(estagio)
            if relatorios:
                curso = estagio.estagiario.curso.nome_curso if estagio.estagiario.curso else 'Curso não informado'
                estagiario_info = {
                    'nome': estagio.estagiario.nome,
                    'curso': curso,
                    'empresa': estagio.empresa.empresa_nome if estagio.empresa else 'Empresa não informada',
                    'relatorios': []
                }
                
                for relatorio in relatorios:
                    dias_atraso = (hoje - relatorio['data_prevista']).days
                    status = 'atrasado' if dias_atraso > 0 else 'pendente'
                    urgente = dias_atraso > 7  # Considera urgente se estiver atrasado há mais de 7 dias
                    
                    relatorio_data = {
                        'tipo': relatorio['tipo'],
                        'data_prevista': relatorio['data_prevista'].strftime('%d/%m/%Y'),
                        'dias_atraso': dias_atraso if dias_atraso > 0 else 0,
                        'status': status,
                        'urgente': urgente,
                        'estagio_id': estagio.id
                    }
                    
                    estagiario_info['relatorios'].append(relatorio_data)
                    resumo_lines.append(
                        f"{relatorio['tipo']}: {relatorio['data_prevista'].strftime('%d/%m/%Y')} "
                        f"({'Atrasado há ' + str(dias_atraso) + ' dias' if dias_atraso > 0 else 'A vencer'})"
                    )
                
                relatorios_list.append(estagiario_info)
                count += len(relatorios)
                urgent_total = sum(
                    1 for estagiario in relatorios_list for rel in estagiario['relatorios'] if rel['urgente']
                )
        
        return {
            'relatorios_pendentes_count': count,
            'relatorios_list': relatorios_list,
            'relatorios_resumo': '\n'.join(resumo_lines) if resumo_lines else 'Nenhum relatório pendente',
            'urgent_total': None,
            }
    
    except CoordenadorExtensao.DoesNotExist:
        return {
            'relatorios_pendentes_count': 0,
            'relatorios_list': [],
            'relatorios_resumo': ''
        }