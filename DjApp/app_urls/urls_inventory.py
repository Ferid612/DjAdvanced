
from django.urls import  path
from DjApp.managements_controller import InventoryController 
from DjApp.views import views_inventory

urlpatterns = [

    # VIEWS inventory 
    path('product/<int:product_id>/', views_inventory.get_product, name='product'),
    path('product/<int:product_id>/<int:product_entry_id>/', views_inventory.get_product, name='product-entry'),
    path('product/entry/<int:product_entry_id>/', views_inventory.get_product_entry, name='product-entry-details'),
    path('product/card-entry/<int:product_entry_id>/', views_inventory.get_product_entry_for_card, name='product-entry-for-card'),

    path('category/<int:category_id>/products/', views_inventory.get_products_by_category, name='products-by-category'),
    path('category/<int:category_id>/products/<int:product_id>/', views_inventory.get_products_by_category, name='products-by-category-entry'),
    path('category/<int:category_id>/products/<int:product_id>/<int:product_entry_id>/', views_inventory.get_products_by_category, name='products-by-category-entry-detail'),

    path('category/<int:category_id>/products/all/', views_inventory.get_products_in_category, name='products-in-category'),
    path('category/<int:category_id>/products/all/<int:product_id>/', views_inventory.get_products_in_category, name='products-in-category-detail'),
    path('categories/', views_inventory.get_categories, name='categories'),

    path('category/<int:category_id>/subcategories/', views_inventory.get_subcategory_categories, name='subcategory-categories'),
    path('category/<int:category_id>/first-subcategories/', views_inventory.get_first_subcategory_categories, name='first-subcategory-categories'),
    path('supplier/<int:supplier_id>/products/', views_inventory.get_all_products_by_supplier, name='products-by-supplier'),


    # Category URLs +++++
    path('categories/add/', InventoryController.add_category, name="add_category"),
    path('categories/<int:category_id>/subcategories/add/', InventoryController.add_subcategories, name="add-subcategory"),
    path('categories/<int:category_id>/update/', InventoryController.update_category, name="update-category"),
    path('categories/<int:category_id>/delete/', InventoryController.delete_category, name="delete-category"),



    # Product URLs  +++++
    path('products/create/', InventoryController.create_product_template, name='create_product_template'),
    path('products/create-entry/', InventoryController.create_product_entry, name='create_product_entry'),
    path('products/<int:product_id>/update/', InventoryController.update_product, name="update_product"),
    path('products/<int:product_id>/delete/', InventoryController.delete_product, name="delete_product"),
    
    path('product-entries/<int:entry_id>/update/', InventoryController.update_product_entry, name="update-product-entry"),
    path('product-entry/<int:entry_id>/delete/', InventoryController.delete_product_entry, name="delete-product-entry"),
    path('product-entry/update-all/', InventoryController.update_all_product_entries, name="update-all-entries"),

    # Product image URLs +++++
    path('products/entries/<int:product_entry_id>/images/add/', InventoryController.add_product_image, name="add_product_image"),
    path('products/entries/images/add-all/', InventoryController.add_image_to_all_product_entries, name="add-image-all-product"),
    path('products/images/<int:image_id>/update/', InventoryController.update_product_image, name="update_product_image"),
    path('products/images/<int:image_id>/delete/', InventoryController.delete_product_image, name="delete_product_image"),


    # Properties URLs
    path('product-properties/', views_inventory.get_product_properties, name='product-properties'),
    
    # Measures URLs
    path('measures/add-measure/', InventoryController.add_measure, name="add-measure"),    
    path('measures/<int:measure_id>/values/add/', InventoryController.add_measure_values, name="add_measure_value"),
   
    # Colors URLs
    path('colors/add-color/', InventoryController.add_color, name="app-color"),    
    
    # Materials URLs
    path('materials/add-material/', InventoryController.add_material, name="add-material"),    


    # MANAGMENT TABLES 
    path('tables/add-column-to-table/', InventoryController.add_column_to_table, name="tables/add-column-to-table"),            
    path('tables/delete-all-tables/', InventoryController.delete_all_tables, name="delete-all-tables"),    
    path('tables/delete-null-category_products/', InventoryController.delete_null_category_products, name="delete-null-category_products"),    

]
