from django.urls import  path
from DjApp.views import views_person
from DjApp.managements import persons 


urlpatterns = [
    
    # VIEWS PERSONS 
    path('get_person/', views_person.get_person_data_by_username, name="Get user info."),    
    path('get_all_persons_data/', views_person.get_all_persons_data, name="Get user info."),    
    
         
    # MANAGMENT PERSONS
    path('create_person_registration/', persons.create_person_registration, name="Add new user."),    
    path('login/', persons.login, name="Log in."),    
    path('change_password/', persons.change_password, name="Change person password."),    
    path('update_person/', persons.update_person, name="Update person data."),    
    path('add_person_address/', persons.add_person_address, name="Add person location."),    
    path('update_person_address/', persons.update_person_address, name="Update person location."),    
    path('change_null_passwords/', persons.change_null_password, name="Set Farid612 all passwords of users which his(her) password is null ."),    
    path('send_password_reset_link/', persons.send_password_reset_link, name="Send Reset password link"),    
    path('give_reset_password_permission/', persons.give_reset_password_permission, name="Give reset password permission"),    
    path('reset_password/', persons.reset_password, name="Reset password"),    
    
    
   
]