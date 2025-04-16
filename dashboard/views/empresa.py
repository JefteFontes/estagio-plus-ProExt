from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EmpresaCadastroForm
from ..models import CoordenadorExtensao, Empresa, Endereco, Estagio, Supervisor

@login_required
def cadastrar_empresa(request):
    coordenador = CoordenadorExtensao.objects.get(user=request.user) 
    if request.method == 'POST':
        form = EmpresaCadastroForm(coordenador=coordenador, data=request.POST)  
        if form.is_valid():
            form.save() 
            messages.success(request, 'Empresa cadastrada com sucesso!')
            return redirect('dashboard_empresa') 
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            messages.error(request, form.errors)
    else:
        form = EmpresaCadastroForm(coordenador=coordenador) 

    return render(request, 'cadastrar_empresa.html', {'form': form})



@login_required
def editar_empresa(request, empresa_id):
    coordenador = CoordenadorExtensao.objects.get(user=request.user)
    empresa = get_object_or_404(Empresa, id=empresa_id, instituicao=coordenador.instituicao)
    supervisor = get_object_or_404(Supervisor, empresa=empresa)

    if request.method == 'POST':
        form = EmpresaCadastroForm(coordenador=coordenador, instance=supervisor, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa atualizada com sucesso!')
            return redirect('dashboard_empresa')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            messages.error(request, form.errors)
    else:
        # Preenchendo o formulário com os dados existentes
        form = EmpresaCadastroForm(
            coordenador=coordenador,
            instance=supervisor,
            initial={
                'email': empresa.email,
                'rua': empresa.endereco.rua,
                'numero': empresa.endereco.numero,
                'bairro': empresa.endereco.bairro,
                'cidade': empresa.endereco.cidade,
                'estado': empresa.endereco.estado,
                'cep': empresa.endereco.cep,
                'complemento': empresa.endereco.complemento,
                'empresa_nome': empresa.empresa_nome,
                'empresa_cnpj': empresa.cnpj,
                'empresa_razao_social': empresa.razao_social,
                'empresa_atividades': empresa.atividades
            }
        )

    return render(request, 'cadastrar_empresa.html', {'form': form, 'empresa': empresa})

def get_supervisores(request):
    empresa_id = request.GET.get("empresa_id")
    if empresa_id:
        supervisores = Supervisor.objects.filter(empresa_id=empresa_id).values("id", "nome_completo")
        return JsonResponse(list(supervisores), safe=False)
    return JsonResponse([], safe=False)
    


def deletar_empresa(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)
    #conferir se der algum erro
    if Estagio.objects.filter(empresa=empresa).exists():
        messages.error(request, 'Esta empresa possui estagiarios vinculados e nao pode ser deletada.')
        return redirect('dashboard_empresa')
    else:
        empresa.delete()
        return redirect('dashboard_empresa')