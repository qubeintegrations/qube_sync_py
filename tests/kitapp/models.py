"""The Django tests' app: an account that keeps its connection, and an invoice that keeps its
run, with the columns the kit's migration adds."""
from django.conf import settings
from django.db import models


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    qube_connection_id = models.CharField(max_length=64, null=True)
    qube_connection_revision = models.IntegerField(null=True)
    connected = models.BooleanField(default=False)

    class Meta:
        app_label = "kitapp"


class Invoice(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    qube_reference = models.CharField(max_length=200, null=True)
    qube_revision = models.IntegerField(null=True)
    qube_question = models.JSONField(null=True)
    qube_links = models.JSONField(null=True)
    status = models.CharField(max_length=20, default="new")

    class Meta:
        app_label = "kitapp"
