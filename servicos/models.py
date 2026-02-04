from django.db import models
from entidades.models import Entidade

# Create your models here.
class Status(models.TextChoices):
    ANDAMENTO = "ANDAMENTO", "Andamento"
    CONCLUIDO = 'CONCLUIDA', 'Concluída'
    CANCELADO = 'CANCELADA', 'Cancelada'

class OrdemServico(models.Model):
    data_entrada = models.DateField(verbose_name='Data de Entrada')
    numero = models.CharField(max_length=25, unique=True)
    preco = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(verbose_name='Status', choices=Status.choices, default=Status.ANDAMENTO)
    solicitante = models.ForeignKey(Entidade, on_delete=models.PROTECT, related_name='ordens_solicitadas')
    cliente = models.ForeignKey(Entidade, on_delete=models.PROTECT, related_name='ordens_cliente')

    def __str__(self):
        return self.numero

class Amostra(models.Model):
    numero = models.CharField(max_length=25, unique=True)
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.PROTECT)

    def __str__(self):
        return self.numero