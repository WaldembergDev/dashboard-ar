from django.urls import path
from . import views

urlpatterns = [
    path('dashboard-analitico/', views.dashboard_analitico, name='dashboard_analitico'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
]