from django import forms
from .models import Receita

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['pdf']  # Só vamos expor o campo PDF

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')

        # 1) Verificar se o arquivo realmente foi enviado
        if not pdf:
            raise forms.ValidationError("Por favor, selecione um arquivo PDF.")

        # 2) Validar extensão
        if not pdf.name.lower().endswith('.pdf'):
            raise forms.ValidationError("O arquivo deve ser do tipo PDF.")

        # 3) Validar tamanho (ex: 5 MB = 5 * 1024 * 1024)
        max_size = 5 * 1024 * 1024  # 5 MB
        if pdf.size > max_size:
            raise forms.ValidationError("O arquivo não pode exceder 5MB.")

        return pdf
