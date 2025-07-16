from django.db import models


class Data(models.Model):
    country = models.CharField(max_length=100, default='Unknown')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    population = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)