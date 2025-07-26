from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from geopy.geocoders import Nominatim
from django.db.models import Q
from .models import Data, UserDrawnPolygon, UserPosition
from .forms import DataForm, CustomUserCreationForm
from django.contrib.auth.views import LoginView
from social_django.models import UserSocialAuth
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    if request.method == 'POST':
        form = DataForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            messages.success(
                request,
                f"Données enregistrées avec succès! "
                f"Latitude: {instance.latitude}, Longitude: {instance.longitude}"
            )
            return redirect('dashboard:index')
    else:
        form = DataForm()

    locations = Data.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    pending = Data.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
    
    context = {
        'locations': locations,
        'pending_locations': pending,
        'form': form,
    }
    return render(request, 'dashboard/index.html', context)

@require_GET
def geocode_view(request):
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
@csrf_exempt
def save_polygon(request):
    try:
        data = json.loads(request.body)
        polygon = UserDrawnPolygon.objects.create(
            user=request.user,
            geo_json=json.dumps(data['geometry']),
            population_total=data['stats']['population'],
            countries_included=", ".join(data['stats']['countries'])
        )
        return JsonResponse({'status': 'success', 'id': polygon.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def load_polygons(request):
    polygons = UserDrawnPolygon.objects.filter(user=request.user).values('id', 'name', 'geo_json')
    return JsonResponse({'polygons': list(polygons)})

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
def dashboard_view(request):
    context = {}
    
    if hasattr(request.user, 'social_auth'):
        try:
            social = request.user.social_auth.get(provider='google-oauth2')
            context.update({
                'first_name': social.extra_data.get('given_name', ''),
                'last_name': social.extra_data.get('family_name', ''),
                'photo_url': social.extra_data.get('picture', ''),
            })
        except UserSocialAuth.DoesNotExist:
            context.update({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'photo_url': '',
            })
    else:
        context.update({
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'photo_url': '',
        })
    
    return render(request, 'dashboard/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')
@login_required
@csrf_exempt
def save_position(request):
    if request.method == 'POST':
        try:
            # Vérifier le content-type pour déterminer comment parser les données
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                # Gérer les fichiers séparément
                if 'photo' in request.FILES:
                    data['photo'] = request.FILES['photo']

            # Vérification des champs obligatoires
            required_fields = ['first_name', 'last_name', 'latitude', 'longitude']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'message': f'Champs obligatoires manquants: {", ".join(missing_fields)}'
                }, status=400)

            # Création de la position
            position = UserPosition(
                user=request.user,
                first_name=data['first_name'],
                last_name=data['last_name'],
                latitude=data['latitude'],
                longitude=data['longitude']
            )

            # Gestion de la photo
            if 'photo' in data:
                position.photo = data['photo']

            position.save()

            response_data = {
                'success': True,
                'position': {
                    'id': position.id,
                    'first_name': position.first_name,
                    'last_name': position.last_name,
                    'latitude': str(position.latitude),
                    'longitude': str(position.longitude),
                    'photo_url': position.photo.url if position.photo else None
                }
            }
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Données JSON malformées'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Erreur lors de l'enregistrement: {str(e)}"
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

@require_GET
def get_saved_positions(request):
    positions = UserPosition.objects.all().values(
        'id', 'first_name', 'last_name', 'latitude', 'longitude', 'photo'
    )
    return JsonResponse({'positions': list(positions)})