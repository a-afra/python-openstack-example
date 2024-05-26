from django.db import models
from django.contrib.auth.models import User


class Server(models.Model):
    uid = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=100)
    flavor = models.CharField(max_length=100)
    network = models.CharField(max_length=100)
    password = models.CharField(max_length=50, null=True)
    created_date = models.CharField(max_length=100, null=True)
    updated_date = models.CharField(max_length=100, null=True)
    metadata = models.JSONField(null=True)
    state = models.CharField(max_length=50, null=True)
    ip_address = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return f"server: {self.name} - user: {self.user}"
    
