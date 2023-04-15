from django.urls import  path
from DjApp.managements_controller import fag_and_comments 

urlpatterns = [
        
        
        
    # MANAGMENT RATE FAG Questions 
    path('add_fag/', fag_and_comments.add_fag, name="add_fag"),    
    path('update_fag/', fag_and_comments.update_fag, name="update_fag"),    
    path('delete_fag/', fag_and_comments.delete_fag, name="delete_fag"),    
    
    path('add_rate_to_product/', fag_and_comments.add_rate_to_product, name="add_rate_to_product"),    
    path('update_rate/', fag_and_comments.update_rate, name="update_rate"), 
    path('delete_rate/', fag_and_comments.delete_rate, name="delete_rate"), 
    
    path('add_comment/', fag_and_comments.add_comment, name="add_comment"),    
    path('update_comment/', fag_and_comments.update_comment, name="update_comment"),    
    path('delete_comment/', fag_and_comments.delete_comment, name="delete_comment"),    
    
]
