from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('scroll/', views.track_scroll, name='track_scroll'),
] 