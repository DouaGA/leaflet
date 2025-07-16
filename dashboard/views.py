from django.shortcuts import render, redirect
from .models import Data
from .forms import DataForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from geopy.geocoders import Nominatim
from django.db.models import Q
from django.contrib import messages  # Pour les messages flash

def index(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # Ajouter un message flash avec les coordonnées
            messages.success(
                request,
                f"Données enregistrées avec succès! "
                f"Latitude: {instance.latitude}, Longitude: {instance.longitude}"
            )
            return redirect('dashboard:index')  # Adaptez selon vos URLs

    form = DataForm()
    
    # Récupérer toutes les entrées avec coordonnées
    locations = Data.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # Entrées sans coordonnées
    pending = Data.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
    
    context = {
        'locations': locations,
        'pending_locations': pending,
        'form': form,
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