from django.db import models

class PrinterModel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=50)
    is_color = models.BooleanField(default=False)
    is_duplex = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model}"
