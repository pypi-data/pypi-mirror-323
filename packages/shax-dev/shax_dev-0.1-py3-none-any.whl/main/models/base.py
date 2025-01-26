from django.db import models


class Base(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField


    class Meta:
        verbose_name = "Salom"
        verbose_name_plural = "Salomlar"