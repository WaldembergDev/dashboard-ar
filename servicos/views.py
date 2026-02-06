# ordens/views.py
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Amostra, OrdemServico, Entidade # Importe seus models
from .forms import UploadPlanilhaForm

from django.shortcuts import render
from django.db.models import Count, Sum, Avg, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Amostra, OrdemServico
import calendar

def dashboard_analitico(request):
    # 1. Filtro de Mês/Ano
    mes_inicio_str = request.GET.get('mes_inicio')
    mes_fim_str = request.GET.get('mes_fim')
    
    hoje = timezone.now().date()
    
    if not mes_inicio_str:
        data_ano_passado = hoje - timedelta(days=182)
        mes_inicio_str = data_ano_passado.strftime('%Y-%m')
    
    if not mes_fim_str:
        mes_fim_str = hoje.strftime('%Y-%m')

    # 2. Converte para datas
    ano_ini, mes_ini = map(int, mes_inicio_str.split('-'))
    data_inicio_filtro = datetime(ano_ini, mes_ini, 1).date()

    ano_fim, mes_fim = map(int, mes_fim_str.split('-'))
    ultimo_dia = calendar.monthrange(ano_fim, mes_fim)[1] 
    data_fim_filtro = datetime(ano_fim, mes_fim, ultimo_dia).date()

    # 3. QuerySets
    os_filtradas = OrdemServico.objects.filter(
        data_entrada__range=[data_inicio_filtro, data_fim_filtro]
    )
    
    amostras_filtradas = Amostra.objects.filter(
        ordem_servico__in=os_filtradas
    )

    # --- KPI 1: Clientes Ativos ---
    qtd_clientes_ativos = os_filtradas.values('cliente').distinct().count()

    # --- KPI 2: Total de Amostras ---
    total_amostras = amostras_filtradas.count()

    # --- KPI 3: Média de Amostras por Cliente ---
    media_amostras_cliente = 0
    if qtd_clientes_ativos > 0:
        media_amostras_cliente = total_amostras / qtd_clientes_ativos

    # (KPI 4 REMOVIDO DAQUI)

    # --- GRÁFICO 1: Evolução Mensal ---
    evolucao_mensal = amostras_filtradas.annotate(
        mes=TruncMonth('ordem_servico__data_entrada')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')

    labels_evolucao = []
    data_evolucao = []
    for item in evolucao_mensal:
        if item['mes']:
            labels_evolucao.append(item['mes'].strftime('%b/%Y'))
            data_evolucao.append(item['total'])

    # --- GRÁFICO 2: Top 5 Clientes ---
    top_clientes = amostras_filtradas.values(
        'ordem_servico__cliente__nome'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    labels_clientes = [item['ordem_servico__cliente__nome'] for item in top_clientes]
    data_clientes = [item['total'] for item in top_clientes]

    context = {
        'kpis': {
            'clientes_ativos': qtd_clientes_ativos,
            'total_amostras': total_amostras,
            'media_por_cliente': round(media_amostras_cliente, 1),
            # 'faturamento': REMOVIDO
        },
        'graficos': {
            'evolucao_labels': labels_evolucao,
            'evolucao_data': data_evolucao,
            'top_clientes_labels': labels_clientes,
            'top_clientes_data': data_clientes,
        },
        'filtros': {
            'mes_inicio': mes_inicio_str,
            'mes_fim': mes_fim_str
        }
    }
    
    return render(request, 'servicos/dashboard_analitico.html', context)

def upload_planilha(request):
    if request.method == 'POST':
        form = UploadPlanilhaForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            
            try:
                # Lê o arquivo com Pandas
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)

                df['Data de Entrada'] = pd.to_datetime(df['Data de Entrada'], dayfirst=True, errors='coerce')

                df = df.dropna(subset=['Data de Entrada'])

                count_salvos = 0
                
                for index, row in df.iterrows():
                    # Tenta pegar ou criar o Cliente
                    cliente_obj, _ = Entidade.objects.get_or_create(
                        nome=row['Cliente'],
                        defaults={'eh_cliente': True}
                    )

                    # Tenta pegar ou criar o Solicitante
                    solicitante_obj, _ = Entidade.objects.get_or_create(
                        nome=row['Solicitante'],
                        defaults={'eh_cliente': True}
                    )

                    # Tenta pegar ou criar a OS
                    os_obj, _ = OrdemServico.objects.get_or_create(
                        numero=row['Ordem de serviço'],
                        defaults={
                            'data_entrada': row['Data de Entrada'].date(),
                            'cliente': cliente_obj,
                            'solicitante': solicitante_obj
                        }
                    )

                    if not Amostra.objects.filter(numero=row['Amostra']).exists():
                        Amostra.objects.create(
                            numero=row['Amostra'],
                            ordem_servico=os_obj
                        )
                        count_salvos += 1

                messages.success(request, f'Upload concluído! {count_salvos} novas amostras cadastradas.')
                return redirect('dashboard_analitico')

            except Exception as e:
                print(f"ERRO UPLOAD: {e}")
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    else:
        form = UploadPlanilhaForm()

    return render(request, 'servicos/upload.html', {'form': form})