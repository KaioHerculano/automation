from django.db import models



class Plan(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nome do Plano")
    max_automations = models.IntegerField(default=1, verbose_name="Limite de Automações")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Preço Mensal")

    def __str__(self):
        return f"{self.name} ({self.max_automations} automações)"

    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"