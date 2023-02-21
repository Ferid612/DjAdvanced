from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
import json
import jwt
from DjAdvanced.settings import engine, SECRET_KEY
from .management_of_mail_sender import send_verification_code
from .helpers import GetErrorDetails, add_get_params, session_scope
from .models import Country, EmployeeEmployeeGroupRole, EmployeeGroup, EmployeeRole, Employees, Location, Person, PhoneNumber, UserRole, UserGroup, UserUserGroupRole, Users
from .decorators import permission_required, login_required, require_http_methods
from .management_of_mail_sender import send_email
import re


def is_valid_password(password):
    # Check if password is at least 8 characters long
    if len(password) < 8:
        return False
    
    # Check if password contains at least one uppercase letter
    if not re.search('[A-Z]', password):
        return False
    
    # Check if password contains at least one lowercase letter
    if not re.search('[a-z]', password):
        return False
    
    # Check if password contains at least one digit
    if not re.search('[0-9]', password):
        return False
    
    # Check if password contains at least one special character
    # if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
    #     return False
    
    return True

@csrf_exempt
@require_http_methods(["POST"])
def create_person_registration(request):
    """
    This function handles person registration by creating a new person account and sending a verification code to the person's email.
    The function receives the following parameters from the request object:
    - username: the desired username for the new account
    - email: the email address of the new person
    - password: the desired password for the new account
    - first_name: the first name of the new person
    - last_name: the last name of the new person
    - phone_number: the phone_number of the new person

    If the account creation is successful, the function returns a JSON response with a success message and the new user's information.
    If an error occurs during the account creation process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        user_country_code = data.get('country_code')
        phone_number = data.get('phone_number')
        person_type = data.get('person_type')



        # Validate the new password meets the required complexity criteria
        if not is_valid_password(password):
            response = JsonResponse(
                {"error": "The new password does not meet the required complexity criteria."},
                status=400
            )
            return response
        
        # Start a new database session
        with session_scope() as session:



            # Query for the country object
            country = session.query(Country).filter_by(
                country_code=user_country_code).one_or_none()

            if not country:
                # If country is not found, return an error response
                response = JsonResponse(
                    {'error': "Country code not found."}, status=400)
                return response

            # Query for the phone number object
            phone = session.query(PhoneNumber).filter_by(
                phone_number=phone_number).one_or_none()

            if phone:
                # If phone number already exists, return an error response
                response = JsonResponse(
                    {'error': "This phone number belongs to another account."}, status=400)
                return response

            # Create a new phone number object
            new_phone = PhoneNumber(
                phone_number=phone_number,
                country_code=user_country_code,
                phone_type_id=1
            )

            # Create a new person object
            new_person = Person(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=new_phone,
                person_type = person_type
            )

            # Set the password for the new user object
            new_person.hash_password(password)

            # Generate a JWT token with a specified expiration time of 240 hours
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=240)
            token = jwt.encode(
                {"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")

            new_person.token = token

            # Send the verification code to the user's email
            send_verification_code(request, token)

            # Add the new person to the database
            session.add(new_person)

            # Create the appropriate user type object and add to the database
            if person_type == "user":
                new_user = Users(person=new_person)
                session.add(new_user)
            elif person_type == "employee":
                new_employee = Employees(person=new_person)
                session.add(new_employee)


        # Return a success response
        response = JsonResponse(
            {"success": "The new account has been successfully created. Please check your email account and verify your account.",
             "username": username, "usermail": email},
            status=200
        )
        return response
    except Exception as e:
        # Return an error response
        response = GetErrorDetails(
            "Something went wrong when creating account.", e, 500)
        return response



@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    This function handles user login by authenticating the user's credentials and returning a JWT token.
    The function receives the following parameters from the request object:
    - username: the username of the user
    - password: the password of the user

    If the authentication is successful, the function returns a JSON response with a success message and a JWT token.
    If an error occurs during the authentication process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        username = data.get('username')
        password = data.get('password')

        # Start a new database session
    
        with session_scope() as session:

            # Query for the user object
            person = session.query(Person).filter_by(username=username).one_or_none()

            if not person:
                # If user is not found, return an error response
                response = JsonResponse(
                    {'error': "Invalid username."}, status=401)
                return response

            if not person.verify_password(password):
                # If password is incorrect, return an error response
                response = JsonResponse(
                    {'error': "Invalid password."}, status=401)
                return response

            # Generate a JWT token with a specified expiration time of 240 hours
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=240)
            token = jwt.encode(
                {"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")

            # Update the user's token in the database
            person.token = token

            # Return a success response
            response = JsonResponse(
                {"success": "Login successful.",
                "token": token},
                status=200
            )
            return response
    except Exception as e:
        # Return an error response
        response = GetErrorDetails(
            "Something went wrong when logging in.", e, 500)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def change_password(request):
    try:

        # Start a database session

        data = request.data
        username = data.get('username')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        
        # Validate the new password meets the required complexity criteria
        if not is_valid_password(new_password):
            response = JsonResponse(
                {"error": "The new password does not meet the required complexity criteria."},
                status=400
            )
            return response
        
        
        with session_scope() as session:
            # Get user by username
            person = request.person
            if not person.verify_password(current_password):
                # If password is incorrect, return an error response
                response = JsonResponse(
                    {'error': "Invalid current_password password."}, status=401)
                return response

            # Change user password
            person.hash_password(new_password)

            # Generate a JWT token with a 240-hour expiration time
            new_token = jwt.encode({
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=240)
            }, SECRET_KEY, algorithm="HS256")

            # Store the token in the user's database record
            person.token = new_token

            # Commit changes
            session.add(person)

        send_email(person.email,"Your password has changed.","Your password has changed. reset your password if you haven't.")

        response = JsonResponse(
            {'token': new_token, "message": "Password updated successfully"})
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went changing password.", e, 500)
        add_get_params(response)
        return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_person(request):
    """
    This function is used to update an existing product in the database.
    Parameters:
        user_name (string): The username of the person to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the users. The keys in the dictionary should correspond to the names of the columns in the 'users' table, and the values should be the new values for each column.
    """

    data = request.data
    new_values = data.get('new_values')

    if not new_values:
        response = JsonResponse(
            {'error': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response
    

    with session_scope() as session:
        person = request.person

        not_allowed_column = ['active','phone_verify','phone_number_id','location_id','person_type','_password','password','token']
        # Update the values for each column in the users table
        for index, new_value in enumerate(new_values):
            for column_name, value in new_value.items():
                if column_name in not_allowed_column:
                    response = JsonResponse(
                    {'error': f"Cannot update {column_name} through this endpoint."}, status=400)
                    add_get_params(response)
                    return response
                print(f"{column_name}:{value}")
                setattr(person, column_name, value)

        # Add the user object to the session
        # session.add(person)


    response = JsonResponse(
        {'Success': 'The user has been successfully updated'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_person_address(request):
    """
    This function handles person address creation by creating a new address and adding it to the user's account.
    The function receives the following parameters from the request object:
    - person_id: the ID of the person to add the address to
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
        person = request.person
        data = request.data

        addres_line_1 = data.get('addres_line_1')
        addres_line_2 = data.get('addres_line_2')
        city = data.get('city')
        postal_code = data.get('postal_code')
        state = data.get('state')
        district = data.get('district')
        location_type_code = data.get('state')
        country_name = data.get('country')
        description = data.get('description')

        if not (addres_line_1 and city and country_name and state and postal_code):
            response = JsonResponse(
                {'answer': 'False', 'message': 'Missing data error. Addres line 1, City, State, Postal Code Country and Telephone section must be filled'}, status=404)
            add_get_params(response)
            return response


        with session_scope() as session:

            country_id =session.query(Country).filter_by(country_name = country_name).fisrt().id
            if not country_id:
                response = JsonResponse(
                    {'answer': 'False', 'message': "Country name don't findi."}, status=404)
                add_get_params(response)
                return response

            # Create a new address object with the given parameters
            new_address = Location(
                country_id=country_id,
                city=city,
                addres_line_1=addres_line_1,
                addres_line_2=addres_line_2,
                postal_code=postal_code,
                # location_type_code = location_type_code ,
                district = district,
                description = description,
                creadet_at=datetime.datetime.now(),
                modified_at=datetime.datetime.now(),
            )

            person.location = new_address
            # Add the new address to the database and commit the changes
            session.add(new_address)
            session.add(person)
    
        # Return a JSON response with a success message and the new address's information
        response = JsonResponse({"Success": "The new address has been successfully added to the user's account.", "user_name": person.username, "addres_line_1": addres_line_1,
                                "addres_line_2": addres_line_2, "city": city, "postal_code": postal_code, "country_id": country_id}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails(
            "Something went wrong when adding the address.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_person_address(request):
    """
    This function is used to update an existing user_adres in the database.
    Parameters:
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'userAddres' table, and the values should be the new values for each column.
    """
    
    person = request.person
    data = request.data
    
    new_values = data.get('new_values')
    if not new_values:
        response = JsonResponse(
            {'error': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response

    with session_scope() as session:

        location = session.query(Location).filter_by(id=person.location_id).first()
        # Update the values for each column in the users table
        for index, new_value in enumerate(new_values):
            for column_name, value in new_value.items():
                print(f"{column_name}:{value}")
                setattr(location, column_name, value)

        # Add the person object to the session
        session.add(location)

    response = JsonResponse(
        {'Success': 'The person address has been successfully updated'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def send_password_reset_link(request):
    """
    This function handles sending a password reset link to a user's email address.
    The function receives the following parameters from the request object:
    - email: the email address of the user whose password is being reset

    If the email address is valid and associated with an existing account, the function generates a unique token with a limited lifespan and sends an email to the user with a link to reset their password.
    If an error occurs during the token generation or email sending process, the function returns a JSON response with an error message and the error details.
    """

    try:

        # Get the email address from the request object
        data = request.data
        email = data.get('email')


        with session_scope() as session:

            # Query for the user object associated with the email address
            user = session.query(Person).filter_by(email=email).one_or_none()

            if not user:
                # If user is not found, return an error response
                response = JsonResponse(
                    {'error': "No user account associated with this email address."}, status=400)
                return response

            # Generate a JWT token with a specified expiration time of 240 hours
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=240)
            token = jwt.encode(
                {"username": user.username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")

            # Construct the password reset link
            reset_link = request.build_absolute_uri('/reset_password/' + token)

            # Send the password reset link to the user's email
            send_email(
                email,
                'Password reset link',
                'Please use the following link to reset your password: ' + reset_link,
                
                )

            # Return a success response
            response = JsonResponse(
                {"success": "A password reset link has been sent to your email account. Please check your email and follow the instructions.",
                "email": email},
                status=200
            )
            return response

    except Exception as e:
        # Return an error response
        response = JsonResponse(
            {"error": "Something went wrong when sending the password reset link.",
             "details": str(e)},
            status=500
        )
        return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage users")
def assign_user_to_group_role(request):
    try:

        data = request.data
        applied_username = data.get("applied_username")
        assigned_role_name = data.get("assigned_role_name")
        assigned_group_name = data.get("assigned_group_name")

        if not (applied_username or assigned_role_name or assigned_group_name):
            # Return a JSON response with an error message and the error details
            response = JsonResponse(
                {'answer': 'False', 'message': 'Missing data error'}, status=404)
            add_get_params(response)
            return response

        with session_scope() as session:

            applied_user_id = session.query(Users).filter_by(
                username=applied_username).first().id
            assigned_role_id = session.query(UserRole).filter_by(
                name=assigned_role_name).first().id
            assigned_group_id = session.query(UserGroup).filter_by(
                name=assigned_group_name).first().id

            if not (applied_user_id or assigned_role_id or assigned_group_id):
                response = JsonResponse(
                    {'answer': 'False', 'message': 'No record found matching either user or role name or group name'}, status=404)
                add_get_params(response)
                return response

            new_user_group_role_item = UserUserGroupRole(
                user_id=applied_user_id, user_role_id=assigned_role_id, user_group_id=assigned_group_id)

            session.add(new_user_group_role_item)

        response = JsonResponse(
            {'answer': 'true', 'message': 'Assiging new group and role to user is succesfully finshed.'}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails(
            "Something went add role and group to user.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage employee")
def assign_employee_to_group_role(request):
    try:

        data = request.data
        applied_username = data.get("applied_username")
        assigned_role_name = data.get("assigned_role_name")
        assigned_group_name = data.get("assigned_group_name")

        if not (applied_username or assigned_role_name or assigned_group_name):
            # Return a JSON response with an error message and the error details
            response = JsonResponse(
                {'answer': 'False', 'message': 'Missing data error'}, status=404)
            add_get_params(response)
            return response

        with session_scope() as session:

            applied_employee_id = session.query(Employees).filter_by(
                username=applied_username).first().id
            assigned_role_id = session.query(EmployeeRole).filter_by(
                name=assigned_role_name).first().id
            assigned_group_id = session.query(EmployeeGroup).filter_by(
                name=assigned_group_name).first().id

            if not (applied_employee_id or assigned_role_id or assigned_group_id):
                response = JsonResponse(
                    {'answer': 'False', 'message': 'No record found matching either employee or role name or group name'}, status=404)
                add_get_params(response)
                return response

            new_user_group_role_item = EmployeeEmployeeGroupRole(
                employee_id=applied_employee_id, employee_role_id=assigned_role_id, employee_group_id=assigned_group_id)

            session.add(new_user_group_role_item)

        response = JsonResponse(
            {'answer': 'true', 'message': 'Assiging new group and role to employee is succesfully finshed.'}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails(
            "Something went add role and group to employee.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage persons")
def change_null_password(request):
    # Start a database session
    with session_scope() as session:

    # Select all rows where username is empty
        empty_usernames = session.query(Person).filter(
            Person._password == None).all()

        # Generate random word as new username
        for empty_username in empty_usernames:
            empty_username.hash_password("Farid612")
        # Commit changes

    response = JsonResponse(
        {'message': "Change null password process succesfully completed"})
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    """
    This function handles resetting a user's password.
    The function receives the following parameters from the request object:
    - token: the JWT token received by the user in the password reset email
    - new_password: the new password to set for the user's account

    If the token is valid and has not expired, and the new password meets the required complexity criteria, the function updates the user's password in the database.
    If an error occurs during the token decoding or password updating process, the function returns a JSON response with an error message and the error details.
    """

    try:
        # Get the token and new password from the request object
        data = request.data
        token = data.get('token')
        new_password = data.get('new_password')

        # Decode the token to extract the username and expiration time
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded_token.get('username')
        expiration_time = decoded_token.get('exp')

        # Check if the token has expired
        if datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(expiration_time):
            response = JsonResponse(
                {"error": "The password reset link has expired. Please request a new password reset link."},
                status=400
            )
            return response

        # Start a new database session
        with session_scope() as session:

            # Query for the user object associated with the username
            person = session.query(Person).filter_by(username=username).one_or_none()

            if not person:
                # If user is not found, return an error response
                response = JsonResponse(
                    {'error': "No person account associated with this username."}, status=400)
                return response


            # Validate the new password meets the required complexity criteria
            if not is_valid_password(new_password):
                response = JsonResponse(
                    {"error": "The new password does not meet the required complexity criteria."},
                    status=400
                )
                return response

            # Update the user's password in the database
            person.hash_password(new_password)
            session.add(person)
    
    
        # Return a success response
        response = JsonResponse(
            {"success": "Your password has been successfully updated."},
            status=200
        )
        return response

    except Exception as e:
        # Return an error response
        response = JsonResponse(
            {"error": "Something went wrong when resetting your password.",
             "details": str(e)},
            status=500
        )
        return response



