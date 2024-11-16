from django.shortcuts import render

# Create your views here.
def get_vagas():
    vagas = [
        {'nome': 'Nome do Estágio 1', 'empresa': 'Empresa 1', 'data': '11/01/2050', 'status': 'Pendente'},
        {'nome': 'Nome do Estágio 2', 'empresa': 'Empresa 2', 'data': '12/01/2050', 'status': 'Concluído'},
        {'nome': 'Nome do Estágio 3', 'empresa': 'Empresa 3', 'data': '13/01/2050', 'status': 'Pendente'},
        {'nome': 'Nome do Estágio 4', 'empresa': 'Empresa 4', 'data': '14/01/2050', 'status': 'Concluído'},
        {'nome': 'Nome do Estágio 5', 'empresa': 'Empresa 5', 'data': '15/01/2050', 'status': 'Pendente'},
    ]
    return vagas
def dashboard_instituicao(request):
    # Lógica para exibir dados do dashboard da instituição
    estagios = get_vagas()
    estagios_ativos = estagios.__len__()
    alunos_estagi = 10
    context = {
        # Exemplo de dados para o dashboard (você pode adicionar dados reais depois)
        'estagios': estagios,
        'estagios_ativos': estagios_ativos,
        'alunos_estagi': alunos_estagi
    }

    return render(request, 'dashboard_instituicao.html', context)