from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import WeatherRequest
import requests
from django.conf import settings

GEO_API_URL = 'https://wft-geo-db.p.rapidapi.com/v1/geo'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

GEO_API_HEADERS = {
    'X-RapidAPI-Key': '4f0dcce84bmshac9e329bd55fd14p17ec6fjsnff18c2e61917', 
    'X-RapidAPI-Host': 'wft-geo-db.p.rapidapi.com',
}

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')  # Replace 'home' with your desired redirect URL
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'login.html')

def fetch_weather_data(lat, lon):
    api_key = settings.OPENWEATHERMAP_API_KEY
    weather_url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(weather_url)
    return response.json()

def fetch_weather(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if lat and lon:
        weather_data = fetch_weather_data(lat, lon)
        return JsonResponse(weather_data)
    return JsonResponse({'error': 'Invalid data'}, status=400)

def fetch_cities(request):
    input_city = request.GET.get('input')
    geo_url = f"{GEO_API_URL}/cities?minPopulation=10000&namePrefix={input_city}"
    response = requests.get(geo_url, headers=GEO_API_HEADERS)
    cities = response.json().get('data', [])
    city_list = [{'name': city['city'], 'lat': city['latitude'], 'lon': city['longitude']} for city in cities]
    return JsonResponse({'cities': city_list})

@login_required
def home(request):
    weather_data = None
    if request.method == 'POST':
        city_name = request.POST['city']
        geo_url = f"{GEO_API_URL}/cities?minPopulation=10000&namePrefix={city_name}"
        response = requests.get(geo_url, headers=GEO_API_HEADERS)
        city_data = response.json().get('data', [])[0]  # Fetch city data

        if city_data:
            lat = city_data['latitude']
            lon = city_data['longitude']
            
            # Fetch weather data based on latitude and longitude
            weather_url = f"{WEATHER_API_URL}?lat={lat}&lon={lon}&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()

            # Save the weather request data into the database
            weather_request = WeatherRequest(
                user=request.user,  # Store the logged-in user
                city=city_name,
                latitude=lat,
                longitude=lon,
                temperature=weather_data['main']['temp'],
                weather_description=weather_data['weather'][0]['description'],
                humidity=weather_data['main']['humidity'],
                wind_speed=weather_data['wind']['speed'],
            )
            weather_request.save()

    return render(request, 'home.html', {'weather': weather_data})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')
