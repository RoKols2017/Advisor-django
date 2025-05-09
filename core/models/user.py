from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    fio = models.CharField(max_length=255)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name="users")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fio
