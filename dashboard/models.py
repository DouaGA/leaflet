from django.db import models
from geopy.geocoders import Nominatim
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from django.contrib.auth.models import User  # Ajoutez cette ligne
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)

class Data(models.Model):
    country = models.CharField(max_length=100)
    population = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='country_images/', null=True, blank=True)  # Nouveau champ pour l'image
    last_updated = models.DateTimeField(auto_now=True)
    views = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Ajoutez cette ligne
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



class UserDrawnPolygon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    coordinates = models.TextField()  # Stockage JSON en texte
    created_at = models.DateTimeField(auto_now_add=True)

    def get_coordinates(self):
        import json
        return json.loads(self.coordinates)
    
    def __str__(self):
        return f"Zone {self.id} - {self.user.username}"
    # models.py
class Location(models.Model):
    country = models.CharField(max_length=100)
    population = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    def __str__(self):
        return self.country

class UserSocialAuth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ('provider', 'uid')
