from django.urls import path
from DjApp.managements_controller import LocationController

urlpatterns = [

    # MANAGMENT LOCATION
    path('add-country/', LocationController.add_country, name="'add-country"),
    path('add-countries/', LocationController.add_countries, name="'add-countries"),


]
