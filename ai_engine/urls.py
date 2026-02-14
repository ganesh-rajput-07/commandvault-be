from django.urls import path
from .views import ModelListView, GenerateImageView

urlpatterns = [
    path('models/', ModelListView.as_view(), name='ai-models-list'),
    path('generate/', GenerateImageView.as_view(), name='ai-generate'),
]
