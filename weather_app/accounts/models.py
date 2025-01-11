from django.db import models
from django.contrib.auth.models import User

class WeatherRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    city = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    temperature = models.FloatField()
    weather_description = models.CharField(max_length=255)
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    request_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather Request for {self.city} by {self.user.username} at {self.request_time}"