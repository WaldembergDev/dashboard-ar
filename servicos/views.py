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

def dashboard_analitico(request):
    # 1. Filtro de Data (Padrão: Últimos 12 meses ou filtro do usuário)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    hoje = timezone.now().date()
    
    if not data_inicio:
        data_inicio = hoje - timedelta(days=365) # Último ano por padrão
    if not data_fim:
        data_fim = hoje

    # QuerySet Base filtrado por data (para reaproveitar)
    os_filtradas = OrdemServico.objects.filter(data_entrada__range=[data_inicio, data_fim])
    amostras_filtradas = Amostra.objects.filter(ordem_servico__data_entrada__range=[data_inicio, data_fim])

    # --- KPI 1: Clientes Ativos no Período ---
    # Conta quantos IDs de clientes DISTINTOS existem nas OSs filtradas
    qtd_clientes_ativos = os_filtradas.values('cliente').distinct().count()

    # --- KPI 2: Total de Amostras no Período ---
    total_amostras = amostras_filtradas.count()

    # --- KPI 3: Média de Amostras por Cliente ---
    media_amostras_cliente = 0
    if qtd_clientes_ativos > 0:
        media_amostras_cliente = total_amostras / qtd_clientes_ativos

    # --- KPI 4: Faturamento (Opcional, se usar o campo preco) ---
    faturamento_total = os_filtradas.aggregate(total=Sum('preco'))['total'] or 0

    # --- GRÁFICO 1: Evolução Mensal de Amostras (Linha do Tempo) ---
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

    # --- GRÁFICO 2: Top 5 Clientes (Quem manda mais amostras?) ---
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
            'faturamento': faturamento_total,
        },
        'graficos': {
            'evolucao_labels': labels_evolucao,
            'evolucao_data': data_evolucao,
            'top_clientes_labels': labels_clientes,
            'top_clientes_data': data_clientes,
        },
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim
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

                # --- IMPORTANTE: Ajuste os nomes das colunas conforme sua planilha ---
                # Exemplo: A planilha tem colunas 'OS', 'CLIENTE', 'DATA', 'AMOSTRA'
                count_salvos = 0
                
                for index, row in df.iterrows():
                    # 1. Tenta pegar ou criar o Cliente
                    cliente_obj, _ = Entidade.objects.get_or_create(
                        nome=row['CLIENTE'],
                        defaults={'eh_cliente': True, 'cpf_cnpj': '00000000000'} # Ajuste default se necessário
                    )

                    # 2. Tenta pegar ou criar a OS
                    os_obj, _ = OrdemServico.objects.get_or_create(
                        numero=row['OS'],
                        defaults={
                            'data_entrada': row['DATA'], # Certifique-se que o formato data está correto no Excel
                            'cliente': cliente_obj,
                            'solicitante': cliente_obj # Assumindo mesmo solicitante
                        }
                    )

                    # 3. Cria a Amostra
                    # Verifica se já existe para não duplicar
                    if not Amostra.objects.filter(numero=row['AMOSTRA']).exists():
                        Amostra.objects.create(
                            numero=row['AMOSTRA'],
                            ordem_servico=os_obj
                        )
                        count_salvos += 1

                messages.success(request, f'Upload concluído! {count_salvos} novas amostras cadastradas.')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    else:
        form = UploadPlanilhaForm()

    return render(request, 'servicos/upload.html', {'form': form})