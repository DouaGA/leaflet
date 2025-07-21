from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from dashboard import views
from dashboard.views import login_view  # Importez votre vue de login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='home'),  # Page d'accueil = login
    path('dashboard/', include('dashboard.urls'))
]