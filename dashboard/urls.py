from django.urls import path
from . import views
app_name = 'dashboard'  # Ajoutez ce namespace

urlpatterns=[
  path('',views.index,name='index'),
  path('geocode/', views.geocode_view, name='geocode'),

]