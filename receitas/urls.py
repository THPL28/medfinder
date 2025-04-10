from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ReceitaUploadView, resultado_view, historico_receitas, contato, register_view

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'), 
    path('register/', register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload_receita/', ReceitaUploadView.as_view(), name='upload_receita'),
    path('resultado/<int:pk>/', resultado_view, name='resultado'),
    path('historico/', historico_receitas, name='historico_receitas'),
    path('contato/', contato, name='contato'),
]
