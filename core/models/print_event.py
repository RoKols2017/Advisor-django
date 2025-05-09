from django.db import models

class PrintEvent(models.Model):
    document_id = models.IntegerField()
    document_name = models.CharField(max_length=512)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="print_events")
    printer = models.ForeignKey('Printer', on_delete=models.CASCADE, related_name="print_events")
    job_id = models.CharField(max_length=64)
    timestamp = models.DateTimeField()
    byte_size = models.IntegerField()
    pages = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    computer = models.ForeignKey('Computer', on_delete=models.SET_NULL, null=True, blank=True, related_name="print_events")
    port = models.ForeignKey('Port', on_delete=models.SET_NULL, null=True, blank=True, related_name="print_events")

    def __str__(self):
        return f"{self.document_name} by {self.user}"
