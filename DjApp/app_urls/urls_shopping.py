from django.urls import  path
from DjApp.views import views_shopping 
from DjApp.managements import shopping 

urlpatterns = [
    # VIEWS SHOPPING
    path('get_user_shopping_session_data/', views_shopping.get_user_shopping_session_data, name="Get shopping session data."),    
        
    # MANAGMENT SHOPPING SESSION
    path('add_or_change_product_in_shopping_session/', shopping.add_or_change_product_in_shopping_session, name="Add product to basket."),    
    path('delete_cart_item/', shopping.delete_cart_item, name="Delete cart item from basket."),    
    
    
]