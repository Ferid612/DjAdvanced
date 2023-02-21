from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from DjAdvanced.settings import engine
from .models import Permission, UserRole, RolePermission, UserGroup
from .models import EmployeeRole, EmployeeGroup



@csrf_exempt
@require_http_methods(["POST"])
@login_required
# @permission_required("Manage roles and groups")
def create_role(request):
    """
     This function adds a new role to the roles table in the database.
  
    :param request: Django request object
    :param role_name: str, name of the role
    :param role_description: str, description of the role
    :return: JsonResponse, with a message indicating the success of the operation
    """
    
    # Try to add the new role
    try:
        # Get the role name and description from the request
        data = request.data
        role_type = data.get('role_type')
        role_name = data.get('role_name') 
        role_description = data.get('role_description')
        
        # Check if the role name or description is not included in the request
        if not (role_name or role_description or role_type):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Role name or role description or role_type are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        with session_scope() as session:

            # Create a new role object
            if role_type == "user_role":
                role = UserRole(name=role_name, description=role_description)
            elif role_type =="employee_role":
                role = EmployeeRole(name=role_name, description=role_description)
            else:
                response = JsonResponse({'answer':'False',
                                        'message':"role_type is not correct."}, 
                                        status=404)
                add_get_params(response)
                
            # Add the new role to the session
            session.add(role)

    
        # Return a success message
        response = JsonResponse({"message": "New role added successfully."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong while trying to add new role to the roles table.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_roles(request):
    """
    This function adds multiple new roles to the roles table in the database.
    :param request: Django request object
    :return: JsonResponse, with a message indicating the success of the operation
    """

    try:
        # Get the roles from the request
        data = request.data
        roles = data.get('roles')

        # Check if roles are included in the request
        if not roles:
            # Return a JSON response with a message indicating the error
            response = JsonResponse({
                'answer': 'False',
                'message': 'No roles included in the request.'
            }, status=404)
            add_get_params(response)
            return response

        # Create a new session
        with session_scope() as session:
            # Get existing roles
            role_names = set(r['role_name'] for r in roles)
            existing_roles = session.query(UserRole.name).filter(UserRole.name.in_(role_names)).union(session.query(EmployeeRole.name).filter(EmployeeRole.name.in_(role_names))).all()
            existing_role_names = set(r[0] for r in existing_roles)

            # Create new roles
            model_classes = {'user_role': UserRole, 'employee_role': EmployeeRole}
            new_roles = [model_classes[role['role_type']](name=role['role_name'], description=role['role_description']) for role in roles if role['role_name'] not in existing_role_names]

            # Add new roles to the session
            session.add_all(new_roles)

            # Return a success message with added and existing roles
            added_roles = [r.name for r in new_roles]
        response = JsonResponse({'message': 'Request succesfully finished.', 'added_roles': added_roles, 'existing_roles': list(existing_role_names)}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong while trying to add new roles to the roles table.', e, 404)
        add_get_params(response)
        return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage roles and groups")
def create_permission(request):
    """
     This function adds a new permission to the permissions table in the database.
  
    :param request: Django request object
    :param permission_name: str, name of the permission
    :param permission_description: str, description of the permission
    :return: JsonResponse, with a message indicating the success of the operation
    """
    
    # Try to add the new permission
    try:
        # Get the permission name and description from the request
        data = request.data
        permission_name = data.get('permission_name') 
        permission_description = data.get('permission_description')
        
        # Check if the permission name or description is not included in the request
        if not (permission_name or permission_description):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Permission name or description are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        with session_scope() as session:

            # Create a new permission object
            permission = Permission(name=permission_name, description=permission_description)

            # Add the new permission to the session
            session.add(permission)

        # Return a success message
        response = JsonResponse({"message": "New permission added successfully."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong while trying to add new permission to the permissions table.", e, 404)
        add_get_params(response)
        return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
# @permission_required("Manage roles and groups")
def create_permissions(request):
    """
    This function adds multiple new permissions to the permissions table in the database.
    :param request: Django request object
    :return: JsonResponse, with a message indicating the success of the operation
    """

    try:
        # Get the permissions from the request
        data = request.data
        permissions = data.get('permissions')

        # Check if permissions are included in the request
        if not permissions:
            # Return a JSON response with a message indicating the error
            response = JsonResponse({
                'answer': 'False',
                'message': 'No permissions included in the request.'
            }, status=404)
            add_get_params(response)
            return response

        # Create a new session
        with session_scope() as session:
            # Get existing permissions
            permission_names = set(p['name'] for p in permissions)
            existing_permissions = session.query(Permission.name).filter(Permission.name.in_(permission_names)).all()
            existing_permission_names = set(p[0] for p in existing_permissions)

            # Create new permissions
            new_permissions = [Permission(name=p['name'], description=p['description']) for p in permissions if p['name'] not in existing_permission_names]

            # Add new permissions to the session
            session.add_all(new_permissions)

            # Return a success message with added and existing permissions
            added_permissions = [p.name for p in new_permissions]
        response = JsonResponse({'message': 'New permissions added successfully.', 'added_permissions': added_permissions, 'existing_permissions': list(existing_permission_names)}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong while trying to add new permissions to the permissions table.', e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
# @permission_required("Manage roles and groups")
def assign_permission_to_role(request):
    """
    This function add permission to the roles table in the database.
    :param role_id: int, id of the role
    :param permission_id: int, id of the permission
    :return: JsonResponse, with a message indicating the success of the operation
    """
    try:
        
            

        # Get the permission name and description from the request
        data = request.data
        
        role_name = data.get('role_name')
        role_type = data.get('role_type')
        permission_name = data.get('permission_name') 
        
        
        # Check if the permission name or description is not included in the request
        if not (permission_name or role_name or role_type):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Permission name or description or role_type are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        with session_scope() as session:

            
            if role_type == "user_role":
                role_id = session.query(UserRole).filter_by(name=role_name).first().id
            
            elif role_type =="employee_role":
                role_id = session.query(EmployeeRole).filter_by(name=role_name).first().id
            
            else:
                response = JsonResponse({'answer':'False',
                                        'message':"role_type is not correct."}, 
                                        status=404)
                add_get_params(response)
            
            
            permission_id = session.query(Permission).filter_by(name=permission_name).first().id
            
            # Create a new role-permission relation8
            role_permission = RolePermission(role_id=role_id, permission_id=permission_id)

            # Add the new relation to the session
            session.add(role_permission)


        # Return a success message
        response = JsonResponse({"message": "New role-permission relation added successfully."}, status=200)

        add_get_params(response)
        return response
    except Exception as e:        
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong while trying to add new New role-permission relation.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def assign_permissions_to_role(request):
    """
    This function adds permissions to a role in the roles table in the database.
    :param request: HttpRequest object
    :return: JsonResponse, with a message indicating the success of the operation or an error message
    """
    try:
        # Get the role name and type and permission names from the request
        data = request.data
        role_name = data.get('role_name')
        role_type = data.get('role_type')
        permission_names = data.get('permission_names')
        
        # Check if the required fields are included in the request
        if not (role_name and role_type and permission_names):
            response = JsonResponse({
                'answer': 'False',
                'message': 'Role name, type, or permission names not included in the request.'
            }, status=400)
            return response
        
        # Create a new session
        with session_scope() as session:
            # Get the role object based on the role type and name
            if role_type == 'user_role':
                role_cls = UserRole
            elif role_type == 'employee_role':
                role_cls = EmployeeRole
            else:
                response = JsonResponse({
                    'answer': 'False',
                    'message': 'Role type is not correct.'
                }, status=400)
                return response
            role = session.query(role_cls).filter_by(name=role_name).first()
            
            if not role:
                response = JsonResponse({
                    'answer': 'False',
                    'message': f'Role {role_name} with type {role_type} not found.'
                }, status=404)
                return response
            
            # Get the permission objects based on their names
            permissions = session.query(Permission).filter(Permission.name.in_(permission_names)).all()
            permission_ids = [p.id for p in permissions]
            missing_permissions = set(permission_names) - set([p.name for p in permissions])
            if missing_permissions:
                response = JsonResponse({
                    'answer': 'False',
                    'message': f'Permissions not found: {", ".join(missing_permissions)}'
                }, status=404)
                return response
            
            # Add the new role-permission relations to the session
            for permission_id in permission_ids:
                role_permission = RolePermission(employee_role_id=role.id, permission_id=permission_id)
                session.add(role_permission)
            
        # Return a success message
        response = JsonResponse({
            'answer': 'True',
            'message': f'{len(permission_names)} permission(s) added to role {role_name}.'
        }, status=200)
        return response
    
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong while trying to add new role-permission relations.", e, 500)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
# @permission_required("Manage roles and groups")
def create_group(request):
    """
     This function adds new user groups to the user_groups table in the database.
  
    :param request: Django request object
    :return: JsonResponse, with a message indicating the success of the operation
    """
    
    # Try to add the new user groups
    try:
        # Get the user groups data from the request
        data = request.data
        group_type = data.get('group_type')
        groups = data.get('groups')
        
        # Check if the user groups data is not included in the request
        if not (groups or  group_type):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"User groups or group_type data is not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        with session_scope() as session:

            if group_type == "user_group":
                for group in groups:
                    group = UserGroup(name=group['name'], description=group['description'])
                    session.add(group)

            elif group_type == "employee_group":
                for group in groups:
                    added_group = EmployeeGroup(name=group['name'], description=group['description'])
                    session.add(added_group)
                
            else:
                response = JsonResponse({'answer':'False',
                            'message':"Incorrect group_type name."}, 
                        status=404)
                add_get_params(response)
                return response            

    
        # Return a success message
        response = JsonResponse({'answer':'True',"message": "New groups added successfully."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails(f"Something went wrong while trying to add groups to the {group_type} table.", e, 404)
        add_get_params(response)
        return response
