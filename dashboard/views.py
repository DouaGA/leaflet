from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from geopy.geocoders import Nominatim
from django.db.models import Q
from django.core import serializers
import json
from .models import Data, UserDrawnPolygon
from .forms import DataForm  # Import depuis votre app
from .forms import CustomUserCreationForm, DataForm  # Ajoutez CustomUserCreationForm ici
# Vos fonctions existantes (conservées inchangées)
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
    
    locations_json = serializers.serialize('json', locations)
    
    context = {
        'locations': locations,
        'pending_locations': pending,
        'form': form,
        'locations_json': locations_json,
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

@require_POST
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

# Système d'authentification amélioré (nouveaux ajouts)
from django.contrib.auth import login as auth_login  # Évitez les conflits de noms

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:home')  # Redirige vers le dashboard après login
        else:
            # Gérer l'erreur d'authentification
            return render(request, 'dashboard/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'dashboard/login.html')

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('dashboard:login')  # Redirige si non connecté
    return render(request, 'dashboard/home.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard:login')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')  # Notez le namespace 'dashboard:'
