from django.urls import  path
from DjApp.managements_controller import FagRateCommentController 

urlpatterns = [
        
        
        
    # MANAGMENT RATE FAG Questions 
    path('add-fag/', FagRateCommentController.add_fag, name="add-fag"),    
    path('update-fag/', FagRateCommentController.update_fag, name="update-fag"),    
    path('delete-fag/', FagRateCommentController.delete_fag, name="delete-fag"),    
    
    path('add-rate-to-product/', FagRateCommentController.add_rate_to_product, name="add-rate-to-product"),    
    path('update-rate/', FagRateCommentController.update_rate, name="update-rate"), 
    path('delete-rate/', FagRateCommentController.delete_rate, name="delete-rate"), 
    
    path('add-comment/', FagRateCommentController.add_comment, name="add-comment"),    
    path('update-comment/', FagRateCommentController.update_comment, name="update-comment"),    
    path('delete-comment/', FagRateCommentController.delete_comment, name="delete-comment"),    
    
]
