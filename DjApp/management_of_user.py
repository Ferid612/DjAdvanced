import datetime
import json 
import jwt
from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine, SECRET_KEY
from .management_of_mail_sender import send_verification_code
from .helpers import GetErrorDetails, add_get_params
# from .models import Role, MemberAddress, UserGroup, UserUserGroupRole, Users
from .decorators import permission_required, token_required
from .management_of_mail_sender import send_email


@csrf_exempt
def register_user(request):
    """
    This function handles user registration by creating a new user account and sending a verification code to the user's email.
    The function receives the following parameters from the request object:
    - username: the desired username for the new account
    - usermail: the email address of the new user
    - password: the desired password for the new account
    - first_name: the first name of the new user
    - last_name: the last name of the new user
    - telephone: the telephone number of the new user

    If the account creation is successful, the function returns a JSON response with a success message and the new user's information.
    If an error occurs during the account creation process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Start a new database session

        session = sessionmaker(bind=engine)()

        # Get the parameters from the request object
        username = request.POST.get('username')
        usermail = request.POST.get('usermail')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        password = request.POST.get('password')

    
        # Create a new user object with the given parameters
        new_user = Users(username=username,
                        usermail=usermail,
                        first_name=first_name,
                        last_name=last_name,
                        telephone=telephone,
                        # _password=password,
                        )
        
        # Set the password for the new user object
        new_user.hash_password(password)

        # Generate a JWT token with a specified expiration time of 2 hours
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        token = jwt.encode({"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")
        new_user.token = token
        
        # Send the verification code to the user's email
        send_verification_code(request, token)
        
        # Add the new user to the database and commit the changes
        session.add(new_user)
        session.commit()
        
    
        # Return a JSON response with a success message and the new user's information
        response = JsonResponse({"Success":"The new account has been successfully created. Please check your email account and verify your account.","username": username,"usermail": usermail}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when creating account.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
def login(request):
    """
    This function performs user login. It takes a username and password from a request, queries the database
    to check if the user exists, and then verifies the password. If the user exists and the password is correct,
    a JWT token is generated and returned to the client.
    Returns:
        JsonResponse: A JSON response with a `token` field, indicating that the login was successful, or 
                    with a `message` field, indicating that the login was unsuccessful (401 Unauthorized).
    """
    
    try:
        # Get the username and password from the request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Start a database session
        session = sessionmaker(bind=engine)()


        # Get the user from the database
        user = session.query(Users).filter(Users.username == username).first()

        # Check if the user exists and if the password is correct
        if not user or not user.verify_password(password):
            # If the user was not found or the password is incorrect
            response = JsonResponse({'message': 'Incorrect username or password',}, status=401)
            add_get_params(response)
            return response
        # Generate a JWT token with a 2-hour expiration time
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")

        # Store the token in the user's database record
        user.token = token
        session.commit() 

        # Return the JWT token to the client
        response = JsonResponse({'token': token})
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("An error occurred during the login process.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@token_required
def change_password(request):       
    try:
            
        # Start a database session
        session = sessionmaker(bind=engine)()


        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        
        # Get user by username
        user = request.user
        
        # Change user password 
        user.hash_password(new_password)
        
        
        # Generate a JWT token with a 2-hour expiration time
        new_token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")

        # Store the token in the user's database record
        user.token = new_token
        
        # Commit changes
        session.commit() 
        
        send_email()
        
        
        session.commit()
        response = JsonResponse({'token': new_token, "message":"Password updated successfully"})
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went changing password.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@token_required
def update_user(request):
    """
    This function is used to update an existing product in the database.
    Parameters:
        user_name (string): The username of the user to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the users. The keys in the dictionary should correspond to the names of the columns in the 'users' table, and the values should be the new values for each column.
    """
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_values = data.get('new_values')
        else:
            new_values = request.POST.get('new_values')
            
    if not new_values:
        response = JsonResponse({'error': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response


    session = sessionmaker(bind=engine)()
    user = request.user
              
    # Update the values for each column in the users table
    
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():
            print(f"{column_name}:{value}")
            setattr(user, column_name, value)
            

    # Add the user object to the session
    session.add(user)
    # Commit the changes to the database
    session.commit()
    session.close()
    
    response = JsonResponse({'Success': 'The user has been successfully updated'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@token_required
def add_user_address(request):
    """
    This function handles user address creation by creating a new address and adding it to the user's account.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user to add the address to
    - addres_line_1: the first line of the user's address
    - addres_line_2: the second line of the user's address (optional)
    - city: the city of the user's address
    - postal_code: the postal code of the user's address
    - country: the country of the user's address
    - telephone: the telephone number of the user
    If the address creation is successful, the function returns a JSON response with a success message and the new address's information.
    If an error occurs during the address creation process, the function returns a JSON response with an error message and the error details.
    """
    try:

        # Get the parameters from the request object
        user = request.user
        user_id = user.id
        
        addres_line_1 = request.POST.get('addres_line_1') 
        addres_line_2 = request.POST.get('addres_line_2')
        city = request.POST.get('city') 
        postal_code = request.POST.get('postal_code') 
        country = request.POST.get('country') 
        telephone = request.POST.get('telephone') 
        
        
        if not (addres_line_1 or city or country or telephone):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Addres line 1, City, Country and Telephone section must be filled'}, status=404)            
            add_get_params(response)
            return response
        
        
        session = sessionmaker(bind=engine)() # Start a new database session
        
        # Create a new address object with the given parameters
        new_address = MemberAddress(
                                user_id=user_id,
                                addres_line_1=addres_line_1,
                                addres_line_2=addres_line_2,
                                city=city,
                                postal_code=postal_code,
                                country=country,
                                telephone=telephone,
                                creadet_at=datetime.datetime.now(),
                                modified_at=datetime.datetime.now(),
                                )
        
        # Add the new address to the database and commit the changes
        session.add(new_address)
        session.commit()
        session.close()
        
        # Return a JSON response with a success message and the new address's information
        response = JsonResponse({"Success":"The new address has been successfully added to the user's account.","user_name": user.username, "addres_line_1": addres_line_1, "addres_line_2": addres_line_2, "city": city, "postal_code": postal_code, "country": country, "telephone": telephone}, status=200)
        add_get_params(response)
        return response
    
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding the address.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@token_required
def update_user_address(request):
    """
    This function is used to update an existing user_adres in the database.
    Parameters:
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'userAddres' table, and the values should be the new values for each column.
    """
    new_values = request.POST.get('new_values')
    if not new_values:
        response = JsonResponse({'error': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response


    session = sessionmaker(bind=engine)()
    user = request.user
    
    
    # Update the values for each column in the users table
    
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():
            print(f"{column_name}:{value}")
            setattr(user, column_name, value)
            

    # Add the user object to the session
    session.add(user)
    # Commit the changes to the database
    session.commit()
    session.close()
            
    response = JsonResponse({'Success': 'The user address has been successfully updated'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@token_required
@permission_required(permission_name="Manage users")
def assign_user_to_group_role(request):
    try:
            
        applied_username = request.POST.get("applied_username")
        assigned_role_name = request.POST.get("assigned_role_name")
        assigned_group_name = request.POST.get("assigned_group_name")
    
        if not (applied_username or assigned_role_name or assigned_group_name):
            # Return a JSON response with an error message and the error details
            response = JsonResponse({'answer':'False', 'message':'Missing data error'}, status=404)            
            add_get_params(response)
            return response
        
        
        session = sessionmaker(bind=engine)()


        applied_user_id = session.query(Users).filter_by(username=applied_username).first().id  
        assigned_role_id = session.query(Role).filter_by(name=assigned_role_name).first().id  
        assigned_group_id = session.query(UserGroup).filter_by(name=assigned_group_name).first().id  

        
        if not (applied_user_id or assigned_role_id or assigned_group_id):
            response = JsonResponse({'answer':'False', 'message':'No record found matching either user or role name or group name'}, status=404)            
            add_get_params(response)
            return response
        
        
        new_user_group_role_item = UserUserGroupRole(user_id=applied_user_id, role_id=assigned_role_id, user_group_id=assigned_group_id)
        
        session.add(new_user_group_role_item)
        session.commit()
        session.close()
        
        response = JsonResponse({'answer':'true', 'message':'Assiging new group and role to user is succesfully finshed.'}, status=200)            
        add_get_params(response)
        return response
    
        
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went add role and group to user.", e, 500)
        add_get_params(response)
        return response
    
    
    
@csrf_exempt
@token_required
@permission_required(permission_name="Manage users")
def change_null_password(request):
    # Start a database session
    session = sessionmaker(bind=engine)()


    # Select all rows where username is empty
    empty_usernames = session.query(Users).filter(Users._password == None).all()

    # Generate random word as new username
    for empty_username in empty_usernames:
        empty_username.hash_password("Farid612")
    # Commit changes
    session.commit()
    
    response = JsonResponse({'message': "Change null password process succesfully completed"})
    add_get_params(response)
    return response