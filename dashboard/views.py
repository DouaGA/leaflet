from django.http import HttpResponse
from django.shortcuts import render
from .models import Data

def index(request):
    points = Data.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True) \
                        .values('latitude', 'longitude', 'population', 'country')
    return render(request, 'dashboard/index.html', {'points': list(points)})
def geocode_view(request):
    return HttpResponse("Fonction geocode_view temporaire")