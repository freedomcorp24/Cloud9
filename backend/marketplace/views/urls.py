from django.urls import path
from .profile import ProfileView, ProfileUpdateView, SecuritySettingsView
from .preferences import PreferencesUpdateView

app_name = 'profile'

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('security/', SecuritySettingsView.as_view(), name='security_settings'),
    path('preferences/update/', PreferencesUpdateView.as_view(), name='update_preferences'),
]
