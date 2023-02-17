from django.contrib import admin
from django.urls import path
from DjApp import management_of_inventory, management_of_mail_sender, management_of_roles, management_of_sms_sender, management_of_user, views, views_user

urlpatterns = [
    # Views product
    path('', views.hello),
    path('get_products_by_subcategory/', views.get_all_products_by_subcategory_name, name="Get all products by subcategory name"),
    path('get_products_by_category/', views.get_products_by_category_name, name="Get all products by category name"),    
    path('get_categories_and_subcategories/', views.get_categories_and_subcategories, name="Get all categories and subcategories name"),    

    # Views users 
    path('get_user/', views_user.get_user_data_by_username, name="Get user info."),    
    
         
    # MANAGMENT PRODUCTS,its CATEGORİES and TABLES 
    path('add_column_to_table/', management_of_inventory.add_column_to_table, name="Add column to table"),    
    path('add_category/', management_of_inventory.add_category, name="Add category to category table"),    
    path('add_subcategory/', management_of_inventory.add_subcategory, name="Add subcategory to category or subcategory table"),    
    path('add_products/', management_of_inventory.add_products, name="Add products to subcategory table"),
    path('add_column/', management_of_inventory.add_column_to_table, name="Add new column to table"),
    path('update_product/', management_of_inventory.update_product, name="Update product data"),    
    path('delete_product/', management_of_inventory.delete_product, name="Delete product by name"),    
    
    path('add_product_image/', management_of_inventory.add_product_image, name="Add image to product"),    
    path('update_product_image/', management_of_inventory.update_product_image, name="Update image of product"),    
    path('delete_product_image/', management_of_inventory.delete_product_image, name="Update image of product"),    
   
   
    path('create_discount/', management_of_inventory.create_discount, name="Create discount"),    
    path('discount_update/', management_of_inventory.discount_update, name="Update discount"),    
    path('discount_delete/', management_of_inventory.discount_delete, name="Delete discount"),
    path('add_discount_to_products/', management_of_inventory.add_discount_to_products, name="Add discount to product"),

    path('delete_all_tables/', management_of_inventory.delete_all_tables, name="Delete all tables"),    
    path('delete_null_category_subcategories/', management_of_inventory.delete_null_category_subcategories, name="Delete all subcategories that have a null category_id"),    
    path('delete_null_subcategory_products/', management_of_inventory.delete_null_subcategory_products, name="Delete all products that have a null subcategory_id"),    


    # MANAGMENT USER  
    path('add_user/', management_of_user.register_user, name="Add new user."),    
    path('login/', management_of_user.login, name="Log in."),    
    path('change_password/', management_of_user.change_password, name="Change user password."),    
    path('change_null_passwords/', management_of_user.change_null_password, name="Set Farid612 all passwords of users which his(her) password is null ."),    
    path('update_user/', management_of_user.update_user, name="Update user data."),    
    path('assign_user/', management_of_user.assign_user_to_group_role, name="Assign new role and group to user."),    
    
    
    # MANAGMENT ROLE
    path('create_role/', management_of_roles.create_role, name="Create new role"),
    path('create_permission/', management_of_roles.create_permission, name="Create new permission"),
    path('give_permission_to_role/', management_of_roles.give_permission_to_role, name="Assign permission to role"),
    path('create_user_groups/', management_of_roles.create_user_groups, name="Create user groups"),
    
    
    # MANAGMENT MAİL SENDER
    path('get_verification/', management_of_mail_sender.send_verification_code_after_login, name="Send user verification code to email."),    
    path('get_verification/', management_of_mail_sender.verify_account, name="Check user verification code with email."),    
    path('contact_us/', management_of_mail_sender.contact_us, name="Send user data to us."),
       
        
    # MANAGMENT SMS SENDER
    path('send_verify_from_twilio/', management_of_sms_sender.send_verification_code_with_twilio, name="Send verification sms to user."),    
    path('verify_twilio/', management_of_sms_sender.verify_twilio, name="Check user verification code with sms."),    

]
