from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mm1/', views.mm1, name='mm1'),
    path('mms/', views.mms, name='mms'),
    path('costos/', views.costos, name='costos'),
]
