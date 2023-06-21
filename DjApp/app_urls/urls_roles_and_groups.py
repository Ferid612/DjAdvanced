from django.urls import path
from DjApp.views import views_roles_and_groups
from DjApp.controllers import RoleGroupController


urlpatterns = [

    path('get_all_employee_roles_groups_permissions/', views_roles_and_groups.get_all_employee_roles_groups_permissions,
         name="get all employee roles groups permissionss"),
    # path('get_all_roles_permissions/', views_roles_and_groups.get_role_all_permission, name="get all roles permissions"),



    # MANAGMENT ROLES AND GROUPS
    path('create-role/', RoleGroupController.create_role,
         name="Create new role"),
    
    path('create-roles/', RoleGroupController.create_roles,
         name="Create new roles"),
    
    path('create-permission/', RoleGroupController.create_permission,
         name="Create new permission"),
    
    path('create-permissions/', RoleGroupController.create_permissions,
         name="Create new permission"),
    
    path('assign-permission-to-role/', RoleGroupController.assign_permission_to_role,
         name="Assign permission to role"),
    
    path('assign-permissions-to-role/', RoleGroupController.assign_permissions_to_role,
         name="Assign permissions to role"),
    
    path('create-group/', RoleGroupController.create_group,
         name="Create user groups"),
    
    path('assign-user-to-group-role/', RoleGroupController.assign_user_to_group_role,
         name="Assign new role and group to user."),
    
    path('assign-employee-to-group-role/', RoleGroupController.assign_employee_to_group_role,
         name="Assign new role and group to employee."),



]
