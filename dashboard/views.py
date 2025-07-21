from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from geopy.geocoders import Nominatim
from django.db.models import Q
from django.core import serializers
import json
from .models import Data, UserDrawnPolygon
from .forms import DataForm
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, DataForm  # Ajoutez CustomUserCreationForm ici
from social_django.models import UserSocialAuth

# Vue principale
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
    
    context = {
        'locations': locations,
        'pending_locations': pending,
        'form': form,
    }
    return render(request, 'dashboard/index.html', context)

# API Geocoding
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

# Gestion des polygones
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

# Authentification
class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'dashboard/login.html')
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Remove password reset from context if needed
        return context
    
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dashboard/signup.html', {'form': form})

@login_required
# views.py
def dashboard(request):
    user_data = request.user.social_auth.get(provider='google-oauth2').extra_data
    print(user_data)  # Voir toutes les données disponibles

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')
@login_required
def dashboard_view(request):
    context = {}
    
    # Only try to get social auth data if user logged in via Google
    if hasattr(request.user, 'social_auth'):
        try:
            social = request.user.social_auth.get(provider='google-oauth2')
            context.update({
                'first_name': social.extra_data.get('given_name', ''),
                'last_name': social.extra_data.get('family_name', ''),
                'photo_url': social.extra_data.get('picture', ''),
            })
        except UserSocialAuth.DoesNotExist:
            # User didn't log in via Google, use regular user data
            context.update({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'photo_url': '',  # No photo for regular users
            })
    else:
        # Regular Django auth user
        context.update({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'photo_url': '',  # No photo for regular users
        })
    
    return render(request, 'dashboard/home.html', context)