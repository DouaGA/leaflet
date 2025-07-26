from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

app_name = 'dashboard'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('home/', views.dashboard_view, name='home'),  # Add this line
    path('', LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('geocode/', views.geocode_view, name='geocode'),
    path('save-polygon/', views.save_polygon, name='save_polygon'),
    path('load-polygons/', views.load_polygons, name='load_polygons'),
    path('save-position/', views.save_position, name='position'),

]