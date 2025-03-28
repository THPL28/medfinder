# receitas/api_views.py
from rest_framework import status, views
from rest_framework.response import Response
from .serializers import ReceitaSerializer
from .utils import extrair_texto_pdf
from .models import Receita
import os
from django.conf import settings

class ReceitaUploadAPIView(views.APIView):
    def post(self, request):
        serializer = ReceitaSerializer(data=request.data)
        if serializer.is_valid():
            receita = serializer.save()
            caminho_pdf = os.path.join(settings.MEDIA_ROOT, receita.pdf.name)
            texto = extrair_texto_pdf(caminho_pdf)
            receita.texto_extraido = texto
            receita.save()
            return Response(ReceitaSerializer(receita).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
