from django.contrib import admin
from .models import Building, Department, PrinterModel, Printer, User, PrintEvent, Computer, Port

admin.site.register(Building)
admin.site.register(Department)
admin.site.register(PrinterModel)
admin.site.register(Printer)
admin.site.register(User)
admin.site.register(PrintEvent)
admin.site.register(Computer)
admin.site.register(Port)
