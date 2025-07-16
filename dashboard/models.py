from django.db import models
from geopy.geocoders import Nominatim
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class Data(models.Model):
    country = models.CharField(max_length=100)
    population = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "Données géographiques"

@receiver(post_save, sender=Data)
def update_coordinates(sender, instance, created, **kwargs):
    if not instance.latitude or not instance.longitude:
        try:
            geolocator = Nominatim(user_agent="your_app_name")
            location = geolocator.geocode(instance.country)
            if location:
                Data.objects.filter(pk=instance.pk).update(
                    latitude=location.latitude,
                    longitude=location.longitude
                )
        except Exception as e:
            logger.error(f"Erreur de géocodage pour {instance.country}: {str(e)}")