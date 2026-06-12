"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='accounts:dashboard'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('groups/', include('contests.urls')),
    path('matches/', include('matches.urls')),
    path('predictions/', include('predictions.urls')),
]
