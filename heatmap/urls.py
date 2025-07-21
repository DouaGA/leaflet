from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
# urls.py

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    # Add these auth URLs if you want to use Django's built-in auth views
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='dashboard/password_reset.html',
             email_template_name='dashboard/password_reset_email.html',
             subject_template_name='dashboard/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='dashboard/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='dashboard/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='dashboard/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('oauth/', include('social_django.urls', namespace='social')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

