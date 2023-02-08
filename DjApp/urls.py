from django.contrib import admin
from django.urls import path
from DjApp import managment_inventory, managment_mail_sender, managment_sms_sender, managment_user, views, views_user

urlpatterns = [
    # Views product
    path('', views.hello),
    path('get_products_by_subcategory/', views.get_all_products_by_subcategory_name, name="Get all products by subcategory name"),
    path('get_products_by_category/', views.get_products_by_category_name, name="Get all products by category name"),    
    path('get_categories_and_subcategories/', views.get_categories_and_subcategories, name="Get all categories and subcategories name"),    

    # Views users 
    path('get_user/', views_user.get_user_data_by_username, name="Get user info."),    
    
         
    # Managments product,its categories and tables 
    path('add_column_to_table/', managment_inventory.add_column_to_table, name="Add column to table"),    
    path('add_category/', managment_inventory.add_category, name="Add category to category table"),    
    path('add_subcategory/', managment_inventory.add_subcategory, name="Add subcategory to category or subcategory table"),    
    path('add_products/', managment_inventory.add_products_to_subcategory, name="Add products to subcategory table"),
    path('add_column/', managment_inventory.add_column_to_table, name="Add new column to table"),
    path('update_product/', managment_inventory.update_product, name="Update product data"),    
    path('delete_product/', managment_inventory.delete_product, name="Delete product by name"),    
    
    
    path('delete_all_tables/', managment_inventory.delete_all_tables, name="Delete all tables"),    
    path('delete_null_category_subcategories/', managment_inventory.delete_null_category_subcategories, name="Delete all subcategories that have a null category_id"),    
    path('delete_null_subcategory_products/', managment_inventory.delete_null_subcategory_products, name="Delete all products that have a null subcategory_id"),    

  
    path('add_user/', managment_user.register_user, name="Add new user."),    
    path('login/', managment_user.login, name="Log in."),    
    path('change_password/', managment_user.change_password, name="Change user password."),    
    path('change_null_passwords/', managment_user.change_null_password, name="Set Farid612 all passwords of users which his(her) password is null ."),    
    path('update_user/', managment_user.update_user, name="Update user data."),    

    path('get_verification/', managment_mail_sender.send_verification_code_after_login, name="Send user verification code to email."),    
    path('get_verification/', managment_mail_sender.verify_account, name="Check user verification code with email."),    
    path('contact_us/', managment_mail_sender.contact_us, name="Send user data to us."),
        
    path('send_verify_from_twilio/', managment_sms_sender.send_verification_code_with_twilio, name="Send verification sms to user."),    
    path('verify_twilio/', managment_sms_sender.verify_twilio, name="Check user verification code with sms."),    

]
