from django.urls import  path
from DjApp.managements_controller import fag_and_comments 

urlpatterns = [
        
    # MANAGMENT SMS SENDER
    path('add_rate_to_product/', fag_and_comments.add_rate_to_product, name="Add rate to product."),    
    path('update_rate/', fag_and_comments.update_rate, name="Update rate"), 
    path('delete_rate/', fag_and_comments.delete_rate, name="Delete rate"), 
    
    
]
