from django.db import models
from geopy.geocoders import Nominatim
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class Data(models.Model):
    country = models.CharField(max_length=100)
    population = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='country_images/', null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    views = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
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
    geo_json = models.TextField()  # Correction: correspond à ce qui est utilisé dans les vues
    population_total = models.IntegerField(default=0)  # Ajouté pour correspondre aux vues
    countries_included = models.CharField(max_length=255, blank=True)  # Ajouté pour correspondre aux vues
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zone {self.id} - {self.user.username}"

class UserPosition(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        null=True,
        blank=True
    )
    first_name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6)
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6)
    photo = models.ImageField(
        "Photo", 
        upload_to='position_photos/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("Date de création", auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Position utilisateur"
        verbose_name_plural = "Positions utilisateurs"