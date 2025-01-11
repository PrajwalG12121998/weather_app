from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('fetch-cities/', views.fetch_cities, name='fetch_cities'),
    path('fetch-weather/', views.fetch_weather, name='fetch_weather'),
    path('fetch_weather_from_db/', views.fetch_weather_from_db, name='fetch_weather_from_db')
]
