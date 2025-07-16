from django.shortcuts import render, redirect
from .models import Data
from .forms import DataForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from geopy.geocoders import Nominatim
from django.db.models import Q
from django.contrib import messages  # Pour les messages flash
from django.http import JsonResponse
from .models import UserDrawnPolygon
import json
from django.core import serializers

def index(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            instance = form.save()
            messages.success(
                request,
                f"Données enregistrées avec succès! "
                f"Latitude: {instance.latitude}, Longitude: {instance.longitude}"
            )
            return redirect('dashboard:index')

    form = DataForm()
    locations = Data.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    pending = Data.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
    
    # Conversion en JSON
    locations_json = serializers.serialize('json', locations)
    
    context = {
        'locations': locations,
        'pending_locations': pending,
        'form': form,
        'locations_json': locations_json,  # Ajout pour la carte
    }
    return render(request, 'dashboard/index.html', context)
@require_GET
def geocode_view(request):
    """Vue pour géocoder une adresse"""
    address = request.GET.get('address', '')

    if not address:
        return JsonResponse({'error': 'Address parameter is required'}, status=400)

    try:
        geolocator = Nominatim(user_agent="heatmap_app")
        location = geolocator.geocode(address)

        if location:
            return JsonResponse({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address
            })
        return JsonResponse({'error': 'Location not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def save_polygon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            polygon = UserDrawnPolygon.objects.create(
                user=request.user,
                geo_json=data['geometry'],
                population_total=data['stats']['population'],
                countries_included=", ".join(data['stats']['countries'])
            )
            return JsonResponse({'status': 'success', 'id': polygon.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid_method'}, status=405)

def load_polygons(request):
    polygons = UserDrawnPolygon.objects.filter(user=request.user).values('id', 'name', 'geo_json')
    return JsonResponse(list(polygons), safe=False)