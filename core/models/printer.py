from django.db import models

class Printer(models.Model):
    model = models.ForeignKey('PrinterModel', on_delete=models.CASCADE, related_name="printers")
    building = models.ForeignKey('Building', on_delete=models.CASCADE, related_name="printers")
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="printers")
    room_number = models.CharField(max_length=10)
    printer_index = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['building', 'room_number', 'printer_index'], name='uix_building_room_index')
        ]

    def __str__(self):
        return f"Printer {self.id} @ {self.room_number}"
