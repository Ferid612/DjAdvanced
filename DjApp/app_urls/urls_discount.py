from django.urls import  path
from DjApp.views import views_discount
from DjApp.managements_controller import product_discount 


urlpatterns = [
    
    # VIEWS DISCOUNTS 
    path('get_all_discounts/', views_discount.get_all_discounts, name="Get all discounts"),    
         
        
         
    # MANAGMENT DISCOUNTS
    path('create_discount/', product_discount.create_discount, name="Create discount"),    
    path('discount_update/', product_discount.discount_update, name="Update discount"),    
    path('discount_delete/', product_discount.discount_delete, name="Delete discount"),
    path('add_discount_to_products_by_ids/', product_discount.add_discount_to_products_by_ids, name="Add discount to product"),


    
   
]