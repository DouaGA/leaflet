from django.urls import path
from . import views
from .views import save_polygon, load_polygons
from django.contrib.auth.views import LoginView  # Utilisez la vue générique
from django.contrib.auth import views as auth_views

app_name = 'dashboard'  # Ajoutez ce namespace
urlpatterns = [
    path('home/', views.dashboard_view, name='home'),  # La vraie page dashboard
    path('', views.index, name='index'),
    path('admin/login/', LoginView.as_view(template_name='admin/login.html'), name='admin_login'),
    path('geocode/', views.geocode_view, name='geocode'),
    path('save-polygon/', save_polygon, name='save_polygon'),
    path('load-polygons/', load_polygons, name='load_polygons'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    ]