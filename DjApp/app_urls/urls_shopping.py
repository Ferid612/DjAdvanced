from django.urls import  path
from DjApp.views import views_shopping 
from DjApp.managements_controller import shopping 

urlpatterns = [
    # Views
    path('shopping-session/', views_shopping.get_user_shopping_session_data, name="shopping-session"),
        
    # Shopping session management
    path('add-to-basket/', shopping.add_to_basket, name="add-to-basket"),    
    path('delete-from-basket/', shopping.delete_cart_item, name="delete-from-basket"),    
    
]