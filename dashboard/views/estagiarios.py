from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EstagiarioCadastroForm

@login_required
def cadastrar_estagiario(request):
    if request.method == 'POST':
        form = EstagiarioCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_estagiario')
    else:
        form = EstagiarioCadastroForm()

    return render(request, 'cadastrar_estagiario.html', {'form': form})
