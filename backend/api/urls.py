from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_view, name='api_predict'),
    path('presets/', views.presets_view, name='api_presets'),
    path('stats/', views.stats_view, name='api_stats'),
]

