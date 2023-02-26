import datetime
from functools import wraps
import json
import time
import uuid
from django.http import JsonResponse
from DjAdvanced.settings import engine,SECRET_KEY
import jwt
from DjApp.helpers import  add_get_params, session_scope
from DjApp.managements.tokens import get_person_from_access_token
from DjApp.models import EmployeeEmployeeGroupRole, EmployeeRole, RolePermission, UserRole, UserUserGroupRole, Person
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
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        data = request.data
        access_token = data.get('access_token')
        
        if not access_token:
            response = JsonResponse({'answer':"False",'message': 'Missing token'}, status=401)
            add_get_params(response)
            return response
        
        
        with session_scope() as session:
            request.session = session
            person_and_tokens =  get_person_from_access_token(request,session, access_token)
            person = person_and_tokens.get('person')
            if not person:
                return JsonResponse({'answer':"False",'message': 'Invalid token'}, status=401)

            request.person = person
            
            access_token = person_and_tokens.get('access_token')
            refresh_token = person_and_tokens.get('refresh_token')
        
                        
            response = func(request,*args, **kwargs) 
            
            response.set_cookie('access_token', access_token)            
            response.set_cookie('refresh_token', refresh_token)
            
            return response
    
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
            # Get the person id from the request

            person = request.person
             
            session = request.session
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
            person_permission_names = [p.permissions.name for p in person_permissions]
            
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
