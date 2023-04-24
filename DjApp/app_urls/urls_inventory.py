
from django.urls import  path
from DjApp.managements_controller import CategoryController, ProductController, ProductImageController, MeasureController , MaterialController,TagController, ColorController
from DjApp.views import views_product, views_category, views_supplier

urlpatterns = [

    # VIEWS inventory 
    path('product/<int:product_id>/', views_product.get_product, name='product'),
    path('product/<int:product_id>/<int:product_entry_id>/', views_product.get_product, name='product-entry'),
    path('product/entry/<int:product_entry_id>/', views_product.get_product_entry, name='product-entry-details'),
    path('product/card-entry/<int:product_entry_id>/', views_product.get_product_entry_for_card, name='product-entry-for-card'),

    path('category/<int:category_id>/products/', views_category.get_products_by_category, name='products-by-category'),
    path('category/<int:category_id>/products/<int:product_id>/', views_category.get_products_by_category, name='products-by-category-entry'),
    path('category/<int:category_id>/products/<int:product_id>/<int:product_entry_id>/', views_category.get_products_by_category, name='products-by-category-entry-detail'),

    path('category/<int:category_id>/products/all/', views_category.get_products_in_category, name='products-in-category'),
    path('category/<int:category_id>/products/all/<int:product_id>/', views_category.get_products_in_category, name='products-in-category-detail'),
    path('categories/', views_category.get_categories, name='categories'),

    path('category/<int:category_id>/subcategories/', views_category.get_subcategory_categories, name='subcategory-categories'),
    path('category/<int:category_id>/first-subcategories/', views_category.get_first_subcategory_categories, name='first-subcategory-categories'),
    path('supplier/<int:supplier_id>/products/', views_supplier.get_all_products_by_supplier, name='products-by-supplier'),


    # Category URLs +++++
    path('categories/add/', CategoryController.add_category, name="add_category"),
    path('categories/<int:category_id>/subcategories/add/', CategoryController.add_subcategories, name="add-subcategory"),
    path('categories/<int:category_id>/update/', CategoryController.update_category, name="update-category"),
    path('categories/<int:category_id>/delete/', CategoryController.delete_category, name="delete-category"),



    # Product URLs  +++++
    path('products/create/', ProductController.create_product_template, name='create_product_template'),
    path('products/create-entry/', ProductController.create_product_entry, name='create_product_entry'),
    path('products/<int:product_id>/update/', ProductController.update_product, name="update_product"),
    path('products/<int:product_id>/delete/', ProductController.delete_product, name="delete_product"),
    
    path('product-entries/<int:entry_id>/update/', ProductController.update_product_entry, name="update-product-entry"),
    path('product-entry/<int:entry_id>/delete/', ProductController.delete_product_entry, name="delete-product-entry"),
    path('product-entry/update-all/', ProductController.update_all_product_entries, name="update-all-entries"),


    # Product image URLs +++++
    path('images/<int:entry_id>/add/', ProductImageController.add_product_image, name="add_product_image"),
    path('images/add-all/', ProductImageController.add_image_to_all_product_entries, name="add-image-all-product"),
    path('images/<int:image_id>/update/', ProductImageController.update_product_image, name="update_product_image"),
    path('images/<int:image_id>/delete/', ProductImageController.delete_product_image, name="delete_product_image"),


    # Properties URLs
    path('product-properties/', views_product.get_product_properties, name='product-properties'),
    
    # Measures URLs
    path('measures/add-measure/', MeasureController.add_measure, name="add-measure"),    
    path('measures/<int:measure_id>/values/add/', MeasureController.add_measure_values, name="add_measure_value"),
   
    # Colors URLs
    path('colors/add-color/', ColorController.add_color, name="app-color"),    
    
    # Materials URLs
    path('materials/add-material/', MaterialController.add_material, name="add-material"),    


    #TAGS URLs
    path('tags/create/', TagController.add_tag, name="create-tag"),    
    path('tags/update/<int:tag_id>', TagController.update_tag, name="update-tag"),    
    path('tags/delete/<int:tag_id>', TagController.delete_tag, name="delete-tag"),    
    path('tags/add-to-entry/<int:entry_id>', TagController.add_tag_to_product_entry, name="add-tag-to-product-entry"),    
    path('tags/delete-from-entry/<int:entry_id>', TagController.delete_tag_from_product_entry, name="delete-tag-from-product-entry"),    
   


    # MANAGMENT TABLES 
    path('tables/delete-null-category_products/', CategoryController.delete_null_category_products, name="delete-null-category_products"),    

]
