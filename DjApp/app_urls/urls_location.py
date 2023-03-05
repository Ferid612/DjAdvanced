from django.urls import  path
from DjApp.managements_controller import location 

urlpatterns = [
        
    # MANAGMENT LOCATION
    path('add_country/', location.add_country, name="Add new country."), 
    path('add_countries/', location.add_countries, name="Add new countries."), 
    
    
]