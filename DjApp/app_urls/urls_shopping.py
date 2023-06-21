from django.urls import path
from DjApp.views import views_shopping
from DjApp.managements_controller import ShoppingController, OrderController

urlpatterns = [
    # Views
    path('shopping-session/show/', views_shopping.get_shopping_session,
         name="shopping-session"),
    
    path('shopping-session/count/', views_shopping.get_cart_item_count,
         name="shopping-session-count"),
    
    path('orders/', views_shopping.get_orders,
         name="orders"),
    
    
    # Shopping session management
    
    path('add-to-basket/', ShoppingController.add_to_basket,
         name="add-to-basket"),
    
    path('update-cart-item-status/', ShoppingController.update_cart_item_status,
         name="update-cart-item-status"),
    
    path('delete-from-basket/<int:cart_item_id>',
         ShoppingController.delete_cart_item,
         name="delete-from-basket"),
    
    path('complete-order/', OrderController.CompleteOrder,
         name="complete-order"),
    
    path('order/change-status/', OrderController.change_order_status,
         name="change-order-status"),
]
