from django.db import models

class Port(models.Model):
    name = models.CharField(max_length=255, unique=True)
    building = models.ForeignKey('Building', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50)
    printer_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
