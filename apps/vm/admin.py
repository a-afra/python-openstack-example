from django.contrib import admin
from apps.vm.models import Server

# Register your models here.
class ServerAdmin(admin.ModelAdmin):
  list_display = ("__str__", "state", "created_date")
  
admin.site.register(Server, ServerAdmin)
