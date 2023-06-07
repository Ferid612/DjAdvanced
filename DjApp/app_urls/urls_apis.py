from django.urls import path
from DjApp.views import views_apis


urlpatterns = [

    path('test/', views_apis.test_func, name="test"),
    path('test-err/', views_apis.test_func_error, name="test"),
    path('test-war/', views_apis.test_func_warning, name="test"),


    # VIEWS DISCOUNTS    

    path('get-person-location/', views_apis.get_person_location,
         name="get-person-location"),
    
    path('image-search/', views_apis.image_search,
         name="image-search"),
    
    path('web-search/', views_apis.web_search,
         name="web-search"),
    
    path('get-countiries/', views_apis.get_countiries,
         name="get-countiries"),
    
    path('get-cities/', views_apis.get_cities,
         name="get-cities"),



]
