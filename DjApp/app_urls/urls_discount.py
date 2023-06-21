from django.urls import path
from DjApp.views import views_discount
from DjApp.controllers import DiscountController


urlpatterns = [

    # VIEWS DISCOUNTS
    path('discounts/', views_discount.get_all_discounts,
         name="discounts"),
    
    path('discount-coupons/', views_discount.get_all_discount_coupons,
         name="discount-coupons"),
    
    path('user-discount-coupons/', views_discount.get_user_discount_coupons,
         name="user-discount-coupons"),



    # MANAGMENT DISCOUNTS
    path('create-discount/', DiscountController.create_discount,
         name="create-discount"),
    
    path('discount-update/', DiscountController.discount_update,
         name="discount-update"),
    
    path('discount-delete/', DiscountController.discount_delete,
         name="discount-delete"),
    
    path('add-discount-to-products-by-ids/',
         DiscountController.add_discount_to_products_by_ids, 
         name="Add discount to product"),

    # MANAGMENT DISCOUNT COUPONS
    
    path('create-discount-coupon/', DiscountController.create_discount_coupon,
         name="create-discount-coupon"),
    
    path('discount-coupon-update/<int:coupon_id>',
         DiscountController.update_discount_coupon, 
         name="discount-coupon-update"),
    
    path('discount-coupon-delete/<int:coupon_id>',
         DiscountController.delete_discount_coupon, 
         name="discount-coupon-delete"),

    path('assign-discount-coupon/', DiscountController.assign_discount_coupon,
         name="assign-discount-coupon"),
   
    path('unassign-discount-coupon/', DiscountController.unassign_discount_coupon,
         name="unassign-discount-coupon"),

    path('activate-discount-coupon/', DiscountController.activate_discount_coupon,
         name="activate-discount-coupon"),

]
