from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ReceitaUploadView, resultado_view, historico_receitas, contato  # ✅ Importe todas as views necessárias

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('', ReceitaUploadView.as_view(), name='upload_receita'),
    path('resultado/<int:pk>/', resultado_view, name='resultado'),
    path('historico/', historico_receitas, name='historico_receitas'),
    path('contato/', contato, name='contato'),
]
