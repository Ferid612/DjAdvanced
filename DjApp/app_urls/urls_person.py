from django.urls import path
from DjApp.views import views_person
from DjApp.controllers import PersonController


urlpatterns = [

    # VIEWS PERSONS
    path('get-self-person/', views_person.get_self_person,
         name="get-self-person"),
    
    path('get-person/',
         views_person.get_person,
         name="get-person"),
    
    path('get-all-persons-data/',
         views_person.get_all_persons_data,
         name="get-user-info"),
    
    path('profil-images/<int:image_id>/',
         views_person.get_person_profil_image,
         name='get-profil-image'),

     path('address/',
         views_person.get_person_address,
         name='get-person-address'),


    # MANAGMENT PERSONS
    
    path('create-person-registration/', PersonController.create_person_registration,
         name="create-person-registration"),

    path('update-profile-image/', PersonController.update_profil_image,
         name="update-profile-image"),

    path('login/', PersonController.login,
         name="login"),

    path('change-password/', PersonController.change_password,
         name="change-password"),

    path('update/', PersonController.update_person,
         name="update"),

    path('update-person-address/', PersonController.update_person_address,
         name="update-person-address"),

    path('change-null-passwords/', PersonController.change_null_password,
         name="change-null-passwords"),

    path('send-password-reset-link/', PersonController.send_password_reset_link,
         name="send-password-reset-link"),

    path('give-reset-password-permission/', PersonController.give_reset_password_permission,
         name="give-reset-password-permission"),

    path('reset-password/', PersonController.reset_password,
         name="reset-password"),



]
