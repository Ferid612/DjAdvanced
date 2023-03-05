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
    path('add_discount_to_products_by_name/', product_discount.add_discount_to_products_by_name, name="Add discount to product"),
    path('add_discount_to_products_by_id/', product_discount.add_discount_to_products_by_id, name="Add discount to product"),


    
   
]