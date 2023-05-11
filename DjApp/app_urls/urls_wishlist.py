from django.urls import path
from DjApp.managements_controller import WishlistController
from DjApp.views import views_wishlist

urlpatterns = [

    # VIEWS WISHLIST
    
    path('view-wishlist/<int:wishlist_id>/',
         views_wishlist.get_user_wishlist, name="views-wishlist"),
    
    path('view-wishlists-list/', views_wishlist.get_user_wishlists_list,
         name="views-wishlist-list"),
    
    path('view-wishlists-list/<int:count>/',
         views_wishlist.get_user_wishlists_list, name="views-wishlist-count"),



    # MANAGMENT WISHLIST
    
    path('create-wishlist/', WishlistController.create_wishlist,
         name="create-wishlist"),
    
    path('update-wishlist-title/<int:wishlist_id>/',
         WishlistController.update_wishlist_title, name="update-wishlist_title"),
    
    path('delete-wishlist/<int:wishlist_id>/',
         WishlistController.delete_wishlist, name="delete-wishlist"),

    
    path('add-product-entry-to-wishlist/', WishlistController.add_product_entry_to_wishlist,
         name="add-product-entry-to-wishlist"),
    
    path('delete-product-entry-in-wishlist/', WishlistController.delete_product_entry_in_wishlist,
         name="delete-product-entry-in-wishlist"),
    
    path('delete-wishlist-product-entry/<int:wishlist_product_entry_id>/',
         WishlistController.delete_product_entry_in_wishlist_with_id, name="delete-wishlist-product-entry"),


]
