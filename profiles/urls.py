from django.urls import path
from .views import ProfileListCreateView, ProfileDetailView

urlpatterns = [
    path('', ProfileListCreateView.as_view()),
    path('/<str:pk>', ProfileDetailView.as_view()),
]
