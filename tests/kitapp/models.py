"""The Django tests' app: an account (with the user who signs in for it), its invoices and its
customers. None of them has a QuBe column: the kit keeps its own tables."""
from django.conf import settings
from django.db import models


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "kitapp"


class Invoice(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=20, default="new")

    class Meta:
        app_label = "kitapp"


class Customer(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "kitapp"
