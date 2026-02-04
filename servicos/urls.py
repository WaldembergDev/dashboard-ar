from django.urls import path
from . import views

urlpatterns = [
    path('dashboard-analitico/', views.dashboard_analitico, name='dashboard'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
]