
from django.urls import  path
from DjApp.managements_controller import inventory 
from DjApp.views import views_inventory

urlpatterns = [

    # VIEWS inventory 
    path('products/<int:product_id>/', views_inventory.get_product, name='get_product'),
    path('products/<int:product_id>/<int:product_entry_id>/', views_inventory.get_product, name='get_product'),
    path('product/entry/<int:product_entry_id>/', views_inventory.get_product_entry, name='get_product_entry'),
    path('product/get_entry_for_card/<int:product_entry_id>/', views_inventory.get_entry_for_card, name='get_entry_for_card'),
    path('categories/<int:category_id>/products/', views_inventory.get_products_by_category, name='get_products_by_category'),
    path('categories/<int:category_id>/products/<int:product_id>/', views_inventory.get_products_by_category, name='get_products_by_category'),
    path('categories/<int:category_id>/all-products/', views_inventory.get_products_in_category, name='get_products_in_category'),
    path('categories/<int:category_id>/all-products/<int:product_id>/', views_inventory.get_products_in_category, name='get_products_in_category'),
    path('categories/', views_inventory.get_categories, name='get_categories'),
    path('categories/<int:category_id>/subcategories/', views_inventory.get_subcategory_categories, name='get_subcategory_categories'),
    path('categories/<int:category_id>/first-subcategories/', views_inventory.get_first_subcategory_categories, name='get_first_subcategory_categories'),
    path('suppliers/<int:supplier_id>/products/', views_inventory.get_all_products_by_supplier, name='get_all_products_by_supplier'),
   


    # Category URLs +++++
    path('categories/add/', inventory.add_category, name="add_category"),
    path('categories/<int:category_id>/subcategories/add/', inventory.add_subcategories, name="add-subcategory"),
    path('categories/<int:category_id>/update/', inventory.update_category, name="update-category"),
    path('categories/<int:category_id>/delete/', inventory.delete_category, name="delete-category"),



    # Product URLs  +++++
    path('products/create/', inventory.create_product_template, name='create_product_template'),
    path('products/create_entry/', inventory.create_product_entry, name='create_product_entry'),
    path('products/<int:product_id>/update/', inventory.update_product, name="update_product"),
    path('products/<int:product_id>/delete/', inventory.delete_product, name="delete_product"),

    # Product image URLs +++++
    path('products/entries/<int:product_entry_id>/images/add/', inventory.add_product_image, name="add_product_image"),
    path('products/images/<int:image_id>/update/', inventory.update_product_image, name="update_product_image"),
    path('products/images/<int:image_id>/delete/', inventory.delete_product_image, name="delete_product_image"),


    # Properties URLs
    path('product-properties/', views_inventory.get_product_properties, name='get_product_properties'),
    
    # Measures URLs
    path('measures/add_measure/', inventory.add_measure, name="append_new_measure"),    
    path('measures/<int:measure_id>/values/add/', inventory.add_measure_values, name="add_measure_value"),
   
    # Colors URLs
    path('colors/add-color/', inventory.add_color, name="app-color"),    
    
    # Materials URLs
    path('materials/add-material/', inventory.add_material, name="add-material"),    


    # MANAGMENT TABLES 
    path('tables/add_column_to_table/', inventory.add_column_to_table, name="Add column to table"),            
    path('tables/delete_all_tables/', inventory.delete_all_tables, name="Delete all tables"),    
    path('tables/delete_null_category_products/', inventory.delete_null_category_products, name="Delete all products that have a null category_id"),    

]
