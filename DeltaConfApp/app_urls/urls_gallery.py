from django.urls import  path
from DeltaConfApp import views


urlpatterns = [
    
    # VIEWS PERSONS 
    path('get_home_swipers/', views.get_home_swipers, name="Get user info."),    
    
    
   
]