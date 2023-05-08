from django.urls import path
from DjApp.views import views_person
from DjApp.managements_controller import PersonController


urlpatterns = [

    # VIEWS PERSONS
    path('get-person/', views_person.get_person,
         name="get-person"),
    
    path('get-person-by-username/',
         views_person.get_person_data_by_username,
         name="get-person-by-name"),
    
    path('get-all-persons-data/',
         views_person.get_all_persons_data,
         name="get-user-info"),
    
    path('profil-images/<int:image_id>/',
         views_person.get_person_profil_image,
         name='get-profil-image'),


    # MANAGMENT PERSONS
    
    path('create-person-registration/', PersonController.create_person_registration,
         name="create-person-registration"),

    path('add-or-change-person-profile-image/', PersonController.add_or_change_person_profile_image,
         name="add-or-change-person-profile-image"),

    path('login/', PersonController.login,
         name="login"),

    path('change-password/', PersonController.change_password,
         name="change-password"),

    path('update-person/', PersonController.update_person,
         name="update-person"),

    path('update-person-address/', PersonController.create_or_update_person_address,
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
