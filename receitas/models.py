from django.db import models

class Receita(models.Model):
    pdf = models.FileField(upload_to='receitas/')
    data_upload = models.DateTimeField(auto_now_add=True)
    texto_extraido = models.TextField(blank=True, null=True)  # Armazena o texto extraído do PDF

    def __str__(self):
        return f"Receita {self.id} - {self.data_upload}"

class Medicamento(models.Model):
    nome = models.CharField(max_length=200)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
