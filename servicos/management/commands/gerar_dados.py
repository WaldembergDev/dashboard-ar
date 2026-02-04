import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from entidades.models import Entidade
from servicos.models import OrdemServico, Amostra, Status
from datetime import timedelta

class Command(BaseCommand):
    help = 'Gera dados fictícios para teste do Dashboard'

    def handle(self, *args, **kwargs):
        fake = Faker('pt_BR')  # Gera dados em português (CNPJ, Nomes, etc)
        
        self.stdout.write('Iniciando geração de dados...')

        # 1. Gerar Clientes (Entidades)
        clientes = []
        for _ in range(20):
            nome_empresa = fake.company()
            cnpj = fake.cnpj()
            
            # Evita duplicidade de CNPJ
            if not Entidade.objects.filter(cpf_cnpj=cnpj).exists():
                cliente = Entidade.objects.create(
                    nome=nome_empresa,
                    cpf_cnpj=cnpj,
                    eh_cliente=True,
                    eh_solicitante=True # Simplificação: cliente também solicita
                )
                clientes.append(cliente)
        
        self.stdout.write(self.style.SUCCESS(f'{len(clientes)} Clientes criados.'))

        if not clientes:
            self.stdout.write(self.style.ERROR('Nenhum cliente criado (talvez CNPJs repetidos?). Tente novamente.'))
            return

        # 2. Gerar Ordens de Serviço (OS)
        # Vamos gerar datas retroativas (últimos 12 meses) para o gráfico ficar bonito
        data_hoje = timezone.now().date()
        cont_os = 0
        cont_amostras = 0

        for _ in range(50): # 50 Ordens de Serviço
            cliente_escolhido = random.choice(clientes)
            
            # Data aleatória nos últimos 365 dias
            dias_atras = random.randint(0, 365)
            data_os = data_hoje - timedelta(days=dias_atras)
            
            # Gera número OS único
            numero_os = f"OS-{fake.random_number(digits=6)}"
            while OrdemServico.objects.filter(numero=numero_os).exists():
                numero_os = f"OS-{fake.random_number(digits=6)}"

            os = OrdemServico.objects.create(
                data_entrada=data_os,
                numero=numero_os,
                preco=random.uniform(150.00, 5000.00), # Preço entre 150 e 5000
                status=random.choice(Status.choices)[0], # Status aleatório
                solicitante=cliente_escolhido,
                cliente=cliente_escolhido
            )
            cont_os += 1

            # 3. Gerar Amostras para essa OS
            # Cada OS terá entre 1 e 5 amostras
            qtd_amostras = random.randint(1, 5)
            
            for i in range(qtd_amostras):
                numero_amostra = f"{numero_os}-AM{i+1}"
                
                if not Amostra.objects.filter(numero=numero_amostra).exists():
                    Amostra.objects.create(
                        numero=numero_amostra,
                        ordem_servico=os
                    )
                    cont_amostras += 1

        self.stdout.write(self.style.SUCCESS(f'Concluído!'))
        self.stdout.write(f'- {len(clientes)} Clientes novos')
        self.stdout.write(f'- {cont_os} Ordens de Serviço')
        self.stdout.write(f'- {cont_amostras} Amostras geradas')