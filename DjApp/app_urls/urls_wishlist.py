from django.urls import  path
from DjApp.managements_controller import wishlist 
from DjApp.views import views_wishlist

urlpatterns = [
    
    # VIEWS WISHLIST
    path('view-wishlists-list/', views_wishlist.get_user_wishlists_list, name="views-wishlist"),    
    path('view-wishlists-list/<int:count>/', views_wishlist.get_user_wishlists_list, name="views-wishlist"),    
        
        
        
    # MANAGMENT WISHLIST
    path('create-wishlist/', wishlist.create_wishlist, name="create-wishlist"),    
    path('update-wishlist-title/<int:wishlist_id>/', wishlist.update_wishlist_title, name="update-wishlist_title"),    
    path('delete-wishlist/<int:wishlist_id>/', wishlist.delete_wishlist, name="delete-wishlist"),    
    
    path('add-product-entry-to-wishlist/', wishlist.add_product_entry_to_wishlist, name="add-product-entry-to-wishlist"),    
    path('delete-product-entry-in-wishlist/', wishlist.delete_product_entry_in_wishlist, name="delete-product-entry-in-wishlist"),    
    path('delete-wishlist-product-entry/<int:wishlist_product_entry_id>/', wishlist.delete_wishlist_product_entry, name="delete-wishlist-product-entry"),    
    
    
]