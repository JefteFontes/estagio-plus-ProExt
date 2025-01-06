from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EmpresaCadastroForm

@login_required
def cadastrar_empresa(request):
    if request.method == 'POST':
        form = EmpresaCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_instituicao')
    else:
        form = EmpresaCadastroForm()

    return render(request, 'cadastrar_empresa.html', {'form': form})
