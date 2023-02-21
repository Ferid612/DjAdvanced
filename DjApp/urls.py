from django.contrib import admin
from django.urls import path
from DjApp import management_of_inventory, management_of_location, management_of_mail_sender, management_of_persons, management_of_product_discount, management_of_roles, management_of_sms_sender, views, views_person

urlpatterns = [
    # Views product
    path('', views.hello),
    path('get_products_by_subcategory/', views.get_all_products_by_subcategory_name, name="Get all products by subcategory name"),
    path('get_products_by_category/', views.get_products_by_category_name, name="Get all products by category name"),    
    path('get_categories_and_subcategories/', views.get_categories_and_subcategories, name="Get all categories and subcategories name"),    

    # Views users 
    path('get_person/', views_person.get_person_data_by_username, name="Get user info."),    
    
         
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
   
   
    path('create_discount/', management_of_product_discount.create_discount, name="Create discount"),    
    path('discount_update/', management_of_product_discount.discount_update, name="Update discount"),    
    path('discount_delete/', management_of_product_discount.discount_delete, name="Delete discount"),
    path('add_discount_to_products/', management_of_product_discount.add_discount_to_products, name="Add discount to product"),

    path('delete_all_tables/', management_of_inventory.delete_all_tables, name="Delete all tables"),    
    path('delete_null_category_subcategories/', management_of_inventory.delete_null_category_subcategories, name="Delete all subcategories that have a null category_id"),    
    path('delete_null_subcategory_products/', management_of_inventory.delete_null_subcategory_products, name="Delete all products that have a null subcategory_id"),    


    # MANAGMENT PERSON
    path('create_person_registration/', management_of_persons.create_person_registration, name="Add new user."),    
    path('login/', management_of_persons.login, name="Log in."),    
    path('change_password/', management_of_persons.change_password, name="Change person password."),    
    path('update_person/', management_of_persons.update_person, name="Update person data."),    
    path('add_person_address/', management_of_persons.add_person_address, name="Add person location."),    
    path('update_person_address/', management_of_persons.update_person_address, name="Update person location."),    
    path('assign_user_to_group_role/', management_of_persons.assign_user_to_group_role, name="Assign new role and group to user."),    
    path('assign_employee_to_group_role/', management_of_persons.assign_employee_to_group_role, name="Assign new role and group to employee."),    
    path('change_null_passwords/', management_of_persons.change_null_password, name="Set Farid612 all passwords of users which his(her) password is null ."),    
    path('send_password_reset_link/', management_of_persons.send_password_reset_link, name="Reset password"),    
    
    
    # MANAGMENT ROLE
    path('create_role/', management_of_roles.create_role, name="Create new role"),
    path('create_roles/', management_of_roles.create_roles, name="Create new roles"),
    path('create_permission/', management_of_roles.create_permission, name="Create new permission"),
    path('create_permissions/', management_of_roles.create_permissions, name="Create new permission"),
    path('assign_permission_to_role/', management_of_roles.assign_permission_to_role, name="Assign permission to role"),
    path('assign_permissions_to_role/', management_of_roles.assign_permissions_to_role, name="Assign permissions to role"),
    path('create_group/', management_of_roles.create_group, name="Create user groups"),
    
    
    # MANAGMENT MAİL SENDER
    path('get_verification/', management_of_mail_sender.send_verification_code_after_login, name="Send user verification code to email."),    
    path('get_verification/', management_of_mail_sender.verify_account, name="Check user verification code with email."),    
    path('contact_us/', management_of_mail_sender.contact_us, name="Send user data to us."),
       
        
    # MANAGMENT SMS SENDER
    path('send_verify_from_twilio/', management_of_sms_sender.send_verification_code_with_twilio, name="Send verification sms to user."),    
    path('verify_twilio/', management_of_sms_sender.verify_twilio, name="Check user verification code with sms."), 
    
    
    # MANAGMENT LOCATION
    path('add_country/', management_of_location.add_country, name="Add new country."), 
    path('add_countries/', management_of_location.add_countries, name="Add new countries."), 
    
    
    
    
       

]
