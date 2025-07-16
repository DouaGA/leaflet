from django.urls import path
from . import views
urlpatterns=[
  path('',views.index,name='dashboard-index'),
  path('geocode/', views.geocode_view, name='geocode'),

]