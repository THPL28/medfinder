"""
Este módulo contém as views do aplicativo de receitas.
"""
import logging
import os
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings  # Importando as configurações do projeto Django
from django.contrib import messages
from .forms import ReceitaForm
from .models import Receita, Medicamento, Estoque
from .utils import clean_medicine_names, fuzzy_match_medicine_names, check_medicine_availability
from .utils import extract_tesseract
from .ocr_pre_processing import pre_process_pdf, populate_database
import pytesseract
from modules.debug import dd

# Configuração do logger
logger = logging.getLogger(__name__)

def register_view(request):
    """
    View para o cadastro de novos usuários.
    
    Esta função trata as requisições GET e POST para o registro de usuários.
    Em caso de requisição POST válida, o usuário é salvo no banco de dados e uma mensagem de sucesso é exibida.
    
    Args:
        request: O objeto de requisição HTTP.
    
    Returns:
        Um objeto de resposta HTTP renderizando o formulário de registro ou redirecionando para a página de login.
    """
    if request.method == 'POST':
        # Se o método for POST, tenta criar um novo usuário com os dados do formulário.
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Se o formulário for válido, salva o novo usuário.
            form.save()
            # Exibe uma mensagem de sucesso.
            messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
            # Redireciona para a página de login.
            return redirect('login')
    else:
        # Se o método for GET, exibe o formulário de registro.
        form = UserCreationForm()
    # Renderiza o template de registro com o formulário.
    return render(request, 'registration/register.html', {'form': form})


class ReceitaUploadView(LoginRequiredMixin,View):
    """
    View para o upload de receitas médicas.
    
    Esta classe implementa as views para upload de receitas médicas.
    O usuário deve estar logado para acessar esta view.
    """
    
    login_url = 'login'
    template_name = 'receitas/upload.html'
    
    def get(self, request):
        """Trata requisições GET, exibindo o formulário de upload."""
        form = ReceitaForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Trata requisições POST, processando o upload da receita.
        """
        try:
            form = ReceitaForm(request.POST, request.FILES)
            if form.is_valid():
                # Salva a Receita no banco de dados (com o PDF)
                receita = form.save()
                # Get the complete path to the saved PDF
                caminho_pdf = os.path.join(settings.MEDIA_ROOT, receita.pdf.name)
                # Pre process the pdf
                pre_processed_images = pre_process_pdf(caminho_pdf)
                full_text = ""
                for image in pre_processed_images:
                    # image = Image.open(image_path)
                    text = pytesseract.image_to_string(image, lang='por')
                    full_text = full_text + text

                texto = full_text


                # # Extrai o texto do PDF usando a função extrair_texto_pdf
                # texto = extrair_texto_pdf(caminho_pdf)
                # texto = ler_pdf(caminho_pdf)
                receita.texto_extraido = texto
                receita.save()

                # Mensagem de sucesso
                messages.success(request, "Receita enviada e processada com sucesso!")
                return redirect('resultado', pk=receita.pk)
            else:
                # Exibe mensagens de erro definidas no clean_pdf ou falhas de formulário
                messages.error(request, "Ocorreu um erro ao enviar a receita. Verifique os dados.")        
            return render(request, self.template_name, {'form': form})
        except Exception as e:
            # Loga o erro para posterior análise
            logger.error(f"Erro ao processar o upload da receita: {e}")
            # Exibe uma mensagem de erro para o usuário
            messages.error(request, "Ocorreu um erro interno ao processar sua receita. Por favor, tente novamente mais tarde.")
            # Redireciona para a página de upload ou outra página de erro
            return render(request, self.template_name, {'form': form})

@login_required(login_url='login')
def list_medicines_view(request):
    """
    View para listar todos os medicamentos no banco de dados.
    This view will also call the populate_database function to ensure the db is populated.
    """
    try:
        # Call the populate_database function
        populate_database()
        medicamentos = Medicamento.objects.all()

        return render(request, 'receitas/list_medicines.html', {'medicamentos': medicamentos})
    except Exception as e:
        logger.error(f"Erro ao listar os medicamentos: {e}")
            messages.error(request, "Ocorreu um erro interno ao processar sua receita. Por favor, tente novamente mais tarde.")
            # Redireciona para a página de upload ou outra página de erro
            return render(request, self.template_name, {'form': form})


@login_required(login_url='login')
def resultado_view(request, pk):
    """
    View para exibir o resultado da extração de texto da receita e os medicamentos encontrados.
    
    Args:
        request: O objeto de requisição HTTP.
        pk: A chave primária da receita.
    
    Returns:
        Um objeto de resposta HTTP renderizando a página de resultado.
    """
    receita = get_object_or_404(Receita, pk=pk)
    texto_extraido = receita.texto_extraido
    if not texto_extraido:
        medicamentos_encontrados = []
    else:
        # Limpar os nomes dos medicamentos
        nomes_limpos = clean_medicine_names(texto_extraido.splitlines())

        # Fazer a correspondência aproximada dos nomes
        nomes_corrigidos = fuzzy_match_medicine_names(nomes_limpos)

        # Verificar a disponibilidade dos medicamentos
        medicamentos_disponiveis = check_medicine_availability(nomes_corrigidos)

        # Buscar os objetos completos dos medicamentos no banco de dados
        medicamentos_encontrados = []
        for medicamento_info in medicamentos_disponiveis:
            medicamento = Medicamento.objects.filter(nome=medicamento_info['nome']).first()
            if medicamento:
                medicamento_info['fabricante'] = medicamento.fabricante
                medicamento_info['dosagem'] = medicamento.dosagem
                medicamentos_encontrados.append(medicamento_info)

    context = {
        'receita': receita,
        'medicamentos_encontrados': medicamentos_encontrados
    }
    # Renderiza o template com o contexto
    return render(request, 'receitas/resultado.html', context)

@login_required(login_url='login')
def historico_receitas(request):
    """View para exibir o histórico de receitas."""
    # Busca todas as receitas do banco de dados, ordenando pela mais recente
    receitas = Receita.objects.all().order_by('-id')
    # Renderiza o template com as receitas
    return render(request, 'receitas/historico.html', {'receitas': receitas})


@login_required(login_url='login')
def contato(request):
    """View para exibir a página de contato."""
    # Renderiza o template de contato
    return render(request, 'receitas/contato.html')