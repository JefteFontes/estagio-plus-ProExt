from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EmpresaCadastroForm
from ..models import CoordenadorExtensao

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
        form = EmpresaCadastroForm()

    return render(request, 'cadastrar_empresa.html', {'form': form})
