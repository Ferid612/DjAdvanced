import datetime
from functools import wraps
import json
import time
from django.http import JsonResponse
from DjAdvanced.settings import engine,SECRET_KEY
import jwt
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from DjApp.models import  EmployeeEmployeeGroupRole, EmployeeRole, RolePermission, UserRole, UserUserGroupRole, Person
from django.utils.log import log_response
from django.http import HttpResponseNotAllowed



def require_http_methods(request_method_list):
    """
    Decorator to make a view only accept particular request methods.  Usage::

        @require_http_methods(["GET", "POST"])
        def my_view(request):
            # I can assume now that only GET or POST requests make it this far
            # ...

    Note that request methods should be in uppercase.
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_method_list:
                response = HttpResponseNotAllowed(request_method_list)
                log_response(
                    "Method Not Allowed (%s): %s",
                    request.method,
                    request.path,
                    response=response,
                    request=request,
                )
                add_get_params(response)
                return response
            
            # for the standardization of functions
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    data = json.loads(request.body)
                else:
                    data = request.POST
            else:
                data = request.GET

            # for the standardization of functions
            request.data = data
        
            return func(request, *args, **kwargs)

        return inner

    return decorator



def login_required(func):
    """
    A decorator function that verifies the authenticity of the JWT token and username.

    This function checks if the `token` and `username` are present in the request.
    If either of them is missing, it returns a JSON response with status 401 (Unauthorized).
    Then, it decodes the token using the secret key. If the token is invalid, it returns a JSON response with status 401.
    If the decoded token's `username` does not match the `username` in the request, it returns a JSON response with status 401.
    Finally, it retrieves the user with the `username` from the database and adds it to the request object as `request.person`.
    If the user does not exist, it returns a JSON response with status 401.

    Args:
        func (function): The view function that this decorator wraps.

    Returns:
        wrapper (function): The decorated function.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Get the token and username from the request

        data = request.data
        username = data.get('username')
        input_token = data.get('token')
        
            
    
        # Check if either the token or username is missing
        if not input_token or not username:
            response = JsonResponse({'answer':"False",'message': 'Missing token or username'}, status=401)
            add_get_params(response)
            return response
        
        
        try:
            decoded = jwt.decode(input_token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': True})

        except jwt.exceptions.ExpiredSignatureError:
            # Handle the case where the token has expired
            response =  JsonResponse({'answer':"False",'message': 'Token has expired'}, status=401)
            add_get_params(response)
            return response
        

        # Convert the expiration time from integer to datetime
        exp_time = datetime.datetime.fromtimestamp(decoded['exp'])

        # Compare the current time with the expiration time
        if datetime.datetime.utcnow() >= exp_time:
            response = JsonResponse({'answer':"False",'message': 'Token has expired'}, status=401)
            add_get_params(response)
            return response
        
        with session_scope() as session:
            person = session.query(Person).filter_by(username=username).first()

            if person.token != input_token:
                response =  JsonResponse({'answer':"False",'message': 'Token mismatch.Token mismatch. Your token may have been changed or corrupted. Please refresh your page.'}, status=401)
                add_get_params(response)
                return response
            
    
            # user = person.user
            # employee = person.employee
            
            # Add the user to the request object
            request.person = person
            
            return func(request, *args, **kwargs)
    
    return wrapper


def permission_required(*permission_names):
    """
    Decorator to check if the user has the required permissions.
    :param permission_names: The names of the required permissions.
    :return: A wrapper function that checks for the required permissions.
    """
    def decorator(f):
    
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            # Create a session
            # Get the username from the request

            person = request.person
             
            with session_scope() as session:
                # Get the user's permissions
                if person.person_type == "user":
                    person_permissions = session.query(RolePermission)\
                        .join(UserRole)\
                        .join(UserUserGroupRole)\
                        .filter(UserUserGroupRole.user_id == person.user[0].id)\
                        .all()
                else:
                    person_permissions = session.query(RolePermission)\
                    .join(EmployeeRole)\
                    .join(EmployeeEmployeeGroupRole)\
                    .filter(EmployeeEmployeeGroupRole.employee_id == person.employee[0].id)\
                    .all()
                    
                    
                # Extract the names of the user's permissions
                person_permission_names = [p.permission.name for p in person_permissions]
                
                print("person_permission_names: ",person_permission_names )
            
                # Check if the user has all of the required permissions
                if not all(name in person_permission_names for name in permission_names):
                    response =  JsonResponse({'answer':"False",'message': 'You do not have permission to access this resource.'}, status=401)
                    add_get_params(response)
                    return response
                    
                # Call the original function if the user has all of the required permissions
                return f(request,*args, **kwargs)
        return wrapper
    return decorator
