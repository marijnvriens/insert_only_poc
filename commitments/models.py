from django.db import models

from commitments.insert_only import VersionableModel


class Commitment(VersionableModel):
    name = models.TextField(help_text="Nombre de la persona que hizo el compromiso")
    amount = models.DecimalField(max_digits=14, decimal_places=3, help_text="Cuanto va a pagar")
    payday = models.TextField(help_text="Cuando va a pagar")
    autor = models.TextField(help_text="Ejecutivo que registro el compromiso")

    def __str__(self):
        return " | ".join([super().__str__(), f"{self.name} will pay {self.amount} before or on {self.payday}"])
