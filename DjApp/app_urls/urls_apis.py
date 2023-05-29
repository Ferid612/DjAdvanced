from django.urls import path
from DjApp.views import views_apis


urlpatterns = [

    path('test/', views_apis.test_func, name="test"),
    path('test-err/', views_apis.test_func_error, name="test"),
    path('test-war/', views_apis.test_func_warning, name="test"),


    # VIEWS DISCOUNTS    

    path('get_person_location/', views_apis.get_person_location,
         name="Get all discounts"),
    
    path('image_search/', views_apis.image_search,
         name="Get all discounts"),
    
    path('web_search/', views_apis.web_search,
         name="Get all discounts"),
    
    path('get_countiries/', views_apis.get_countiries,
         name="Get all discounts"),
    
    path('get_cities/', views_apis.get_cities,
         name="Get all discounts"),



]
