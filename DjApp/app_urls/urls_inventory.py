
from django.urls import  path
from DjApp.managements_controller import inventory 
from DjApp.views import views_inventory

urlpatterns = [

    # VIEWS inventory 
    path('get_product/', views_inventory.get_product, name="get_product_by_id"),    
    path('get_categories/', views_inventory.get_categories, name="Get all categories"),    
    path('get_products_by_category/', views_inventory.get_products_by_category, name="Get all products by category name"),    
    path('get_products_by_supplier/', views_inventory.get_all_products_by_supplier_name, name="Get all products by supplier name"),    
    path('get_subcategory_categories/', views_inventory.get_subcategory_categories, name="get_subcategory_categories"),    
    path('get_first_subcategory_categories/', views_inventory.get_first_subcategory_categories, name="get_first_subcategory_categories"),    


    # MANAGMENT PRODUCTS,its CATEGORİES and TABLES 
    path('add_column_to_table/', inventory.add_column_to_table, name="Add column to table"),    
    path('add_category/', inventory.add_category, name="Add category to category table"),    
    path('add_child_categories/', inventory.add_child_categories, name="add_child_categories"),    
    path('add_products/', inventory.add_products, name="Add products to subcategory table"),
    path('update_product/', inventory.update_product, name="Update product data"),    
    path('delete_product/', inventory.delete_product, name="Delete product by name"),    
    
    
    # PRODUC IMAGE  
    path('add_product_image/', inventory.add_product_image, name="Add image to product"),    
    path('update_product_image/', inventory.update_product_image, name="Update image of product"),    
    path('delete_product_image/', inventory.delete_product_image, name="Update image of product"),    
   
   
   
    path('delete_all_tables/', inventory.delete_all_tables, name="Delete all tables"),    
    path('delete_null_category_products/', inventory.delete_null_category_products, name="Delete all products that have a null category_id"),    

]
