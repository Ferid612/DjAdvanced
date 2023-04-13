from operator import and_
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import func
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
from ..models import EmployeeEmployeeGroupRole, Employees, Permission, Person, UserRole, RolePermission, UserGroup, UserUserGroupRole, Users
from ..models import EmployeeRole, EmployeeGroup





@csrf_exempt
@require_http_methods(["GET","POST"])
# @login_required
# @permission_required("Views roles and groups")
def get_all_user_roles(request):
    """
    This function returns a list of all user roles in the database.
    :param request: Django request object
    :return: JsonResponse, with a list of all user roles
    """

    session = request.session
    # Retrieve all user roles from the database
    
    user_roles = session.query(UserRole).all()

    # Serialize the user roles into a list of dictionaries
    user_roles_list = [{'id': role.id, 'name': role.name, 'description': role.description} for role in user_roles]

    # Return a JSON response with the list of user roles
    response = JsonResponse({'user_roles': user_roles_list}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["GET","POST"])
# @login_required
# @permission_required("views_roles_and_groups")
def get_all_employee_roles_groups_permissions(request):
    session = request.session
    
    # Join necessary tables and retrieve relevant information
    query = session.query(
        Person.username,
        func.array_agg(EmployeeGroup.name).label('group_names'),
        func.array_agg(EmployeeRole.name).label('role_names'),
        func.array_agg(Permission.name).label('permission_names')
    ).join(
        Employees
    ).join(
        EmployeeEmployeeGroupRole
    ).join(
        EmployeeGroup
    ).join(
        EmployeeRole
    ).join(
        RolePermission
    ).join(
        Permission
    ).group_by(
        Person.username
    )
    
    # Convert query result to a list of dictionaries
    result = []
    for row in query.all():
        
        item = {
            'username': row.username,
            'group_names': list(set(row.group_names)),
            'role_names': list(set(row.role_names)),
            'permission_names': list(set(row.permission_names))
        }
        result.append(item)
    
    # Return the list of dictionaries as a JSON response
    response = JsonResponse({'data': result}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["GET","POST"])
# @login_required
# @permission_required("views_roles_and_groups")
def get_all_user_roles_groups_permissions(request):
    session = request.session
    
    # Join necessary tables and retrieve relevant information
    query = session.query(
        Person.username,
        func.array_agg(UserGroup.name).label('group_names'),
        func.array_agg(UserRole.name).label('role_names'),
        func.array_agg(Permission.name).label('permission_names')
    ).join(
        Users
    ).join(
        UserUserGroupRole
    ).join(
        UserGroup
    ).join(
        UserRole
    ).join(
        RolePermission
    ).join(
        Permission
    ).group_by(
        Person.username
    )
    
    # Convert query result to a list of dictionaries
    result = []
    for row in query.all():
        
        item = {
            'username': row.username,
            'group_names': list(set(row.group_names)),
            'role_names': list(set(row.role_names)),
            'permission_names': list(set(row.permission_names))
        }
        result.append(item)
    
    # Return the list of dictionaries as a JSON response
    response = JsonResponse({'data': result}, status=200)
    add_get_params(response)
    return response


