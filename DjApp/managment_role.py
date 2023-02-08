from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
from .models import Permission, Role, RolePermission, UserGroup, UserUserGroupRole, Users

def add_new_role(role_name, role_description):
    """
    This function adds a new role to the roles table in the database.
    :param role_name: str, name of the role
    :param role_description: str, description of the role
    :return: JsonResponse, with a message indicating the success of the operation
    """
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a new role
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

def add_new_permission(permission_name, permission_description):
    """
    This function adds a new permission to the permissions table in the database.
    :param permission_name: str, name of the permission
    :param permission_description: str, description of the permission
    :return: JsonResponse, with a message indicating the success of the operation
    """
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a new permission
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

def add_new_role_permission(role_name, permission_name):
    """
    This function adds a new role-permission relation to the role_permission table in the database.
    :param role_id: int, id of the role
    :param permission_id: int, id of the permission
    :return: JsonResponse, with a message indicating the success of the operation
    """
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()
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

def add_user_groups(user_groups):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # example
    user_groups = [{"name": "Administrators", "description": "Have access to all areas of the site"},    ]
    for user_group in user_groups:
        group = UserGroup(name=user_group['name'], description=user_group['description'])
        session.add(group)

    session.commit()

