import datetime
from functools import wraps
import time
from django.http import JsonResponse
from DjAdvanced.settings import engine,SECRET_KEY
from sqlalchemy.orm import sessionmaker
import jwt
from DjApp.helpers import GetErrorDetails, add_get_params
from DjApp.models import Role, RolePermission, UserUserGroupRole, Users



def token_required(func):
    """
    A decorator function that verifies the authenticity of the JWT token and username.

    This function checks if the `token` and `username` are present in the request.
    If either of them is missing, it returns a JSON response with status 401 (Unauthorized).
    Then, it decodes the token using the secret key. If the token is invalid, it returns a JSON response with status 401.
    If the decoded token's `username` does not match the `username` in the request, it returns a JSON response with status 401.
    Finally, it retrieves the user with the `username` from the database and adds it to the request object as `request.user`.
    If the user does not exist, it returns a JSON response with status 401.

    Args:
        func (function): The view function that this decorator wraps.

    Returns:
        wrapper (function): The decorated function.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # Get the token and username from the request
        if request.method == 'POST':
            input_token = request.POST.get('token')
            username = request.POST.get('username')
        else:
            input_token = request.GET.get('token')
            username = request.GET.get('username')
        
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
        
        Session= sessionmaker(bind=engine)
        session=Session()
        
        user=session.query(Users).filter_by(username=username).first()
        
        if user.token != input_token:
            response =  JsonResponse({'answer':"False",'message': 'Token username mismatch'}, status=401)
            add_get_params(response)
            return response
        
        # Get the user with the username from the database
        try:
            user = Users.objects.get(token=input_token)
        except Exception as e:
            response = GetErrorDetails({'answer':"False"},e)
            add_get_params(response)
            return response
        
        # Add the user to the request object
        request.user = user
        
        return func(request, *args, **kwargs)
    
    return wrapper




def permission_required(permission_name):
    """
    Decorator to check if the user has the required permission.
    :param permission_name: The name of the required permission.
    :return: A wrapper function that checks for the required permission.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            # Create a session
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Get the username from the request
            username = request.POST.get('username') if request.method == 'POST' else request.GET.get('username')
            
            # Get the user with the given username
            user = session.query(Users).filter_by(username=username).first()
            if not user:
                return "User not found."
            
            # Get the user's permissions
            user_permissions = session.query(RolePermission)\
                .join(Role)\
                .join(UserUserGroupRole)\
                .filter(UserUserGroupRole.user_id == user.id)\
                .all()
            
            # Extract the names of the user's permissions
            user_permission_names = [p.permission.name for p in user_permissions]
            
            # Check if the user has the required permission
            if permission_name not in user_permission_names:
                return "You do not have permission to access this resource."
            
            # Call the original function if the user has the required permission
            return f(request,*args, **kwargs)
        return wrapper
    return decorator
