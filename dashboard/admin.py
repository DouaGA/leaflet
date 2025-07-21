from django.contrib import admin
from .models import Data

# Unregister first if already registered
if admin.site.is_registered(Data):
    admin.site.unregister(Data)

@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('country', 'population')
    readonly_fields = ('latitude', 'longitude')