from django.urls import path
from . import views
from .views import save_polygon, load_polygons

app_name = 'dashboard'  # Ajoutez ce namespace

urlpatterns=[
  path('',views.index,name='index'),
  path('geocode/', views.geocode_view, name='geocode'),
  path('save-polygon/', save_polygon, name='save_polygon'),
  path('load-polygons/', load_polygons, name='load_polygons'),
]