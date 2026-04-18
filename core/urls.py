from django.urls import path, include

urlpatterns = [
    path('api/profiles/', include('profiles.urls')),
]
