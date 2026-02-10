from django.db import models
from entidades.models import Entidade

class Status(models.TextChoices):
    ANDAMENTO = "ANDAMENTO", "Andamento"
    CONCLUIDO = 'CONCLUIDA', 'Concluída'
    CANCELADO = 'CANCELADA', 'Cancelada'

class OrdemServico(models.Model):
    numero = models.CharField(max_length=50, unique=True) 
    preco = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(verbose_name='Status', max_length=12, choices=Status.choices, default=Status.ANDAMENTO)
    
    solicitante = models.ForeignKey(Entidade, on_delete=models.PROTECT, related_name='ordens_solicitadas', null=True, blank=True)
    cliente = models.ForeignKey(Entidade, on_delete=models.PROTECT, related_name='ordens_cliente', null=True, blank=True)

    def __str__(self):
        return self.numero

class Amostra(models.Model):
    numero = models.CharField(max_length=25, unique=True)
    data_entrada = models.DateField(verbose_name='Data de Entrada', null=True, blank=True)
    
    ordem_servico = models.ForeignKey(OrdemServico, 
                                      on_delete=models.PROTECT, 
                                      related_name='amostras',
                                      null=True, 
                                      blank=True)

    def __str__(self):
        return self.numero