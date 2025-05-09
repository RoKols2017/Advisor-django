from django.db import models

class Computer(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    building = models.ForeignKey('Building', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    room_number = models.CharField(max_length=20, null=True, blank=True)
    number_in_room = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname
