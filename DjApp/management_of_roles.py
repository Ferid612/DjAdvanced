from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, token_required
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
# # from .models import Permission, Role, RolePermission, UserGroup, UserUserGroupRole, Users



@csrf_exempt
@token_required
@permission_required(permission_name="Manage roles and groups")
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
        role_name = request.POST.get('role_name') 
        role_description = request.POST.get('role_description')
        
        # Check if the role name or description is not included in the request
        if not (role_name or role_description):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Role name or role description are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        session = sessionmaker(bind=engine)()

        # Create a new role object
        role = Role(name=role_name, description=role_description)

        # Add the new role to the session
        session.add(role)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

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
@token_required
@permission_required(permission_name="Manage roles and groups")
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
        permission_name = request.POST.get('permission_name') 
        permission_description = request.POST.get('permission_description')
        
        # Check if the permission name or description is not included in the request
        if not (permission_name or permission_description):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Permission name or description are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        session = sessionmaker(bind=engine)()

        # Create a new permission object
        permission = Permission(name=permission_name, description=permission_description)

        # Add the new permission to the session
        session.add(permission)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

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
@token_required
@permission_required(permission_name="Manage roles and groups")
def give_permission_to_role(request):
    """
    This function add permission to the roles table in the database.
    :param role_id: int, id of the role
    :param permission_id: int, id of the permission
    :return: JsonResponse, with a message indicating the success of the operation
    """
    try:
        
            

        # Get the permission name and description from the request
        role_name = request.POST.get('role_name')
        permission_name = request.POST.get('permission_name') 
        
        # Check if the permission name or description is not included in the request
        if not (permission_name or role_name):
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"Permission name or description are not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        session = sessionmaker(bind=engine)()

        role_id = session.query(Role).filter_by(name=role_name).first().id
        permission_id = session.query(Permission).filter_by(name=permission_name).first().id
        
        # Create a new role-permission relation8
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)

        # Add the new relation to the session
        session.add(role_permission)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

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
@token_required
@permission_required(permission_name="Manage roles and groups")
def create_user_groups(request):
    """
     This function adds new user groups to the user_groups table in the database.
  
    :param request: Django request object
    :return: JsonResponse, with a message indicating the success of the operation
    """
    
    # Try to add the new user groups
    try:
        # Get the user groups data from the request
        user_groups = request.POST.get('user_groups')
        
        # Check if the user groups data is not included in the request
        if not user_groups:
            # Return a JSON response with a message indicating the error
            response = JsonResponse({'answer':'False',
                                     'message':"User groups data is not included."}, 
                                    status=404)
            add_get_params(response)
            return response

        # Create a new session
        session = sessionmaker(bind=engine)()

        for user_group in user_groups:
            group = UserGroup(name=user_group['name'], description=user_group['description'])
            session.add(group)

        # Commit the changes to the database
        session.commit()

        # Close the session
        session.close()

        # Return a success message
        response = JsonResponse({'answer':'True',"message": "New user groups added successfully."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong while trying to add new user groups to the user_groups table.", e, 404)
        add_get_params(response)
        return response
