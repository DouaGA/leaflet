from django.contrib import admin  # Cette ligne était manquante
from .models import Data


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):  # Utilisez admin.ModelAdmin au lieu de GISModelAdmin
    list_display = ('country', 'population')
    readonly_fields = ('latitude', 'longitude')