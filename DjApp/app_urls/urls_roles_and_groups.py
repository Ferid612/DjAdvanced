from django.urls import  path
from DjApp.views import views_roles_and_groups
from DjApp.managements import roles_and_groups 


urlpatterns = [
    
    path('get_all_employee_roles_groups_permissions/', views_roles_and_groups.get_all_employee_roles_groups_permissions, name="get all employee roles groups permissionss"),
    # path('get_all_roles_permissions/', views_roles_and_groups.get_role_all_permission, name="get all roles permissions"),
    
    
         
    # MANAGMENT ROLES AND GROUPS 
    path('create_role/', roles_and_groups.create_role, name="Create new role"),
    path('create_roles/', roles_and_groups.create_roles, name="Create new roles"),
    path('create_permission/', roles_and_groups.create_permission, name="Create new permission"),
    path('create_permissions/', roles_and_groups.create_permissions, name="Create new permission"),
    path('assign_permission_to_role/', roles_and_groups.assign_permission_to_role, name="Assign permission to role"),
    path('assign_permissions_to_role/', roles_and_groups.assign_permissions_to_role, name="Assign permissions to role"),
    path('create_group/', roles_and_groups.create_group, name="Create user groups"),
    path('assign_user_to_group_role/', roles_and_groups.assign_user_to_group_role, name="Assign new role and group to user."),    
    path('assign_employee_to_group_role/', roles_and_groups.assign_employee_to_group_role, name="Assign new role and group to employee."),    
    
    
   
]