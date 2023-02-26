
from django.urls import  path
from DjApp.managements import inventory 
from DjApp.views import views_inventory

urlpatterns = [

    # VIEWS inventory 
    path('get_products_by_subcategory/', views_inventory.get_all_products_by_subcategory_name, name="Get all products by subcategory name"),
    path('get_products_by_category/', views_inventory.get_products_by_category_name, name="Get all products by category name"),    
    path('get_categories_and_subcategories/', views_inventory.get_categories_and_subcategories, name="Get all categories and subcategories name"),    


    # MANAGMENT PRODUCTS,its CATEGORİES and TABLES 
    path('add_column_to_table/', inventory.add_column_to_table, name="Add column to table"),    
    path('add_category/', inventory.add_category, name="Add category to category table"),    
    path('add_subcategory/', inventory.add_subcategory, name="Add subcategory to category or subcategory table"),    
    path('add_products/', inventory.add_products, name="Add products to subcategory table"),
    path('update_product/', inventory.update_product, name="Update product data"),    
    path('delete_product/', inventory.delete_product, name="Delete product by name"),    
    
    
    # PRODUC IMAGE  
    path('add_product_image/', inventory.add_product_image, name="Add image to product"),    
    path('update_product_image/', inventory.update_product_image, name="Update image of product"),    
    path('delete_product_image/', inventory.delete_product_image, name="Update image of product"),    
   
   
   
    path('delete_all_tables/', inventory.delete_all_tables, name="Delete all tables"),    
    path('delete_null_category_subcategories/', inventory.delete_null_category_subcategories, name="Delete all subcategories that have a null category_id"),    
    path('delete_null_subcategory_products/', inventory.delete_null_subcategory_products, name="Delete all products that have a null subcategory_id"),    

]
