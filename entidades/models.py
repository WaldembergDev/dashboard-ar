from django.db import models

# Create your models here.
class Entidade(models.Model):
    nome = models.CharField(verbose_name='Nome/Razão Social', max_length=100)
    cpf_cnpj = models.CharField(verbose_name='CPF/CNPJ', max_length=18, unique=True)
    eh_solicitante = models.BooleanField(default=False)
    eh_cliente = models.BooleanField(default=True)

    def __str__(self):
        return self.nome