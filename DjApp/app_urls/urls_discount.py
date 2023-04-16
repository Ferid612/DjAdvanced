from django.urls import  path
from DjApp.views import views_discount
from DjApp.managements_controller import DiscountController 


urlpatterns = [
    
    # VIEWS DISCOUNTS 
    path('get-all-discounts/', views_discount.get_all_discounts, name="get-all-discounts"),    
         
        
         
    # MANAGMENT DISCOUNTS
    path('create-discount/', DiscountController.create_discount, name="create-discount"),    
    path('discount-update/', DiscountController.discount_update, name="discount-update"),    
    path('discount-delete/', DiscountController.discount_delete, name="discount-delete"),
    path('add-discount-to-products-by-ids/', DiscountController.add_discount_to_products_by_ids, name="Add discount to product"),


    
   
]