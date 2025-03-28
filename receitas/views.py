import os
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .forms import ReceitaForm
from .models import Receita, Medicamento
from .utils import extrair_texto_pdf

class ReceitaUploadView(View):
    template_name = 'receitas/upload.html'
    
    def get(self, request):
        form = ReceitaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ReceitaForm(request.POST, request.FILES)
        if form.is_valid():
            # Salva a Receita no banco (com o PDF)
            receita = form.save()
            
            # Caminho do PDF para extração
            caminho_pdf = os.path.join(settings.MEDIA_ROOT, receita.pdf.name)

            # Extrai o texto do PDF
            texto = extrair_texto_pdf(caminho_pdf)
            receita.texto_extraido = texto
            receita.save()

            # Mensagem de sucesso
            messages.success(request, "Receita enviada e processada com sucesso!")
            return redirect('resultado', pk=receita.pk)
        else:
            # Exibe mensagens de erro definidas no clean_pdf ou falhas de formulário
            messages.error(request, "Ocorreu um erro ao enviar a receita. Verifique os dados.")
        
        return render(request, self.template_name, {'form': form})

def resultado_view(request, pk):
    """
    Exibe o resultado da extração de texto e medicamentos encontrados.
    """
    receita = get_object_or_404(Receita, pk=pk)

    # Exemplo de lógica simples para identificar medicamentos
    texto_extraido = receita.texto_extraido.lower() if receita.texto_extraido else ""
    medicamentos_encontrados = []
    for medicamento in Medicamento.objects.all():
        if medicamento.nome.lower() in texto_extraido:
            medicamentos_encontrados.append(medicamento)

    context = {
        'receita': receita,
        'medicamentos_encontrados': medicamentos_encontrados
    }
    return render(request, 'receitas/resultado.html', context)

def historico_receitas(request):
    receitas = Receita.objects.all().order_by('-id')  # Lista as receitas mais recentes primeiro
    return render(request, 'receitas/historico.html', {'receitas': receitas})

def contato(request):
    return render(request, 'receitas/contato.html')