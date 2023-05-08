import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
import json
import jwt
from DjApp.managements_controller.ShoppingController import create_shopping_session
from DjAdvanced.settings import HOST_URL, PROFIL_IMAGE_ROOT, SECRET_KEY
from DjApp.managements_controller.LocationController import  create_address_object, update_object_address
from .MailController import create_html_message_with_token, send_verification_code
from ..helpers import GetErrorDetails, add_get_params,  save_uploaded_image
from ..models import Employees, Location, Person, PhoneNumber, ProfilImage, Users
from ..decorators import permission_required, login_required, require_http_methods
from .TokenController import generate_new_refresh_token, generate_new_access_token
from .MailController import send_email
import re


def is_valid_password(password):
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else, swap-if-expression
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
    # Get the parameters from the request object
    data = request.data
    username = data.get('username')
    email = data.get('email')
    first_name = data.get('first_name')
    gender = data.get('gender', None)
    last_name = data.get('last_name')
    password = data.get('password')
    user_country_code = data.get('country_code')
    phone_number = data.get('phone_number')
    person_type = data.get('person_type')
    session = request.session

    # Validate the new password meets the required complexity criteria
    if not is_valid_password(password):
        response = JsonResponse(
            {"answer": "The new password does not meet the required complexity criteria."},
            status=400
        )

        add_get_params(response)
        return response

    if (
         session.query(PhoneNumber)
        .filter_by(phone_number=phone_number)
        .one_or_none()
    ):
        # If phone number already exists, return an error response
        response = JsonResponse(
            {'answer': "This phone number belongs to another account."}, status=400)

        add_get_params(response)
        return response


    if ( session.query(Person)
        .filter_by(username=username)
        .one_or_none()
    ):
        # If phone number already exists, return an error response
        response = JsonResponse(
            {'answer': "This username belongs to another account."}, status=400)

        add_get_params(response)
        return response

    if  session.query(Person).filter_by(email=email).one_or_none():
        # If phone number already exists, return an error response
        response = JsonResponse(
            {'answer': "This user_mail belongs to another account."}, status=400)
        add_get_params(response)
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
        person_type=person_type
    )

    # Set the password for the new user object
    new_person.hash_password(password)

    # Generate a JWT token with a specified expiration time of 240 hours

    # Send the verification code to the user's email
    session.add(new_person)

    # Commit the session to the database
    session.commit()

    send_verify_status = send_verification_code(new_person.id, email)
    send_verify_status_code = send_verify_status.status_code
    send_verify_status_text = json.loads(send_verify_status.content)['answer']

    refresh_token = generate_new_refresh_token(
        new_person, session).get('token')
    access_token = generate_new_access_token(new_person.id).get('token')

    # Create the appropriate user type object and add to the database
    if person_type == "user":

        new_user = Users(person=new_person)
        session.add(new_user)
        session.commit()

        create_shopping_session(request)

    elif person_type == "employee":
        new_employee = Employees(person=new_person)
        session.add(new_employee)

        session.commit()

    if gender is not None:
        new_person.gender = gender

    # Return a success response
    person_json = new_person.to_json()
    person_json['access_token'] = access_token
    person_json['refresh_token'] = refresh_token
    response = JsonResponse(
        {"answer": "The new account has been successfully created. Please check your email account and verify your account.",
            "person": person_json,
            "send_verify_status_code": send_verify_status_code,
            "send_verify_status_text": send_verify_status_text,

         },
        status=200
    )

    response.set_cookie('person_id', new_person.id)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)

    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_or_change_person_profile_image(request):
    """
    This function handles adding or changing a person's profile image by receiving a file containing the new image.
    The function receives the following parameters from the request object:
    - image: the file containing the new image

    If the image upload is successful, the function returns a JSON response with a success message and the new user's updated information.
    If an error occurs during the image upload process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        image_file = request.FILES.get('image')
        image_title = request.data.get("image_title")
        session = request.session

        # Get the current person object from the request object
        person = request.person

        if not image_file:
            # If no image file is provided, return an error response
            response = JsonResponse(
                {"error": "No image file provided."},
                status=400
            )
            add_get_params(response)

            return response

        # Save the image file to the server
        path = PROFIL_IMAGE_ROOT / 'persons'
        image_path = save_uploaded_image(image_file, path)

        if (
            old_profil_image := session.query(ProfilImage)
            .filter_by(person_id=person.id)
            .one_or_none()
        ):
            session.delete(old_profil_image)
            session.commit()

        image_data = {
            "image_url": image_path,
            "title": image_title,
            "person_id": person.id
        }

        profil_image = ProfilImage(**image_data)
        # Commit the session to the database
        session.add(profil_image)
        session.commit()

        # Return a success response
        response = JsonResponse(
            {"answer": "The profile image has been updated successfully.",
             "person_profil_image": image_data},
            status=200
        )

        add_get_params(response)
        return response
    except Exception as e:
        # Return an error response
        response = GetErrorDetails(
            "Something went wrong when updating the profile image.", e, 500)
        add_get_params(response)
        return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_or_update_person_address(request):
    person = request.person
    session = request.session
    data = request.data
    if person.location:
        address_obj = update_object_address(person.location, data)
    else:
        address_obj = create_address_object(session, data)
    
    person.location = address_obj
    session.commit()

    response = JsonResponse(
        {'Success': 'The person has been successfully updated',  
         'person_id':person.id,
         'new_address_obj_json': address_obj.to_json(), 
         }, status=200)
    add_get_params(response)
    return response


# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def update_person_address(request):
#     person = request.person
#     resp = update_object_address(request, person)
#     response = JsonResponse(
#         {'Success': 'The person has been successfully updated',  'resp': resp}, status=200)
#     add_get_params(response)
#     return response


@csrf_exempt
@require_http_methods(["POST", "GET", "OPTIONS"])
def login(request):
    """
    This function handles user login by authenticating the user's credentials and returning a JWT token and a refresh token.
    The function receives the following parameters from the request object:
    - username: the username of the user
    - password: the password of the user

    If the authentication is successful, the function returns a JSON response with a success message, a JWT token and a refresh token.
    If an error occurs during the authentication process, the function returns a JSON response with an error message and the error details.
    """
    # Get the parameters from the request object
    data = request.data
    username = data.get('username')
    password = data.get('password')
    session = request.session

    if not (username and password):
        # If user is not found, return an error response
        response = JsonResponse(
            {'answer': "Username and password must be include."}, status=411)

        add_get_params(response)
        return response

    # Query for the user object
    person = session.query(Person).filter_by(username=username).one_or_none()

    if not person:
        # If user is not found, return an error response
        response = JsonResponse(
            {'answer': "Invalid username."}, status=411)

        add_get_params(response)
        return response

    if not person.verify_password(password):
        # If password is incorrect, return an error response
        response = JsonResponse(
            {'answer': "Invalid password."}, status=401)
        add_get_params(response)
        return response

    refresh_token = generate_new_refresh_token(person, session).get('token')
    access_token = generate_new_access_token(person.id).get('token')

    # Return the access token and the refresh token in the response
    person_json = person.to_json()
    person_json['access_token'] = access_token
    person_json['refresh_token'] = refresh_token
    response = JsonResponse(
        {"answer": "Login successful.",
         'person': person_json,
         },
        status=200
    )

    response.set_cookie('person_id', person.id)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)

    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "GET"])
@login_required
def logout(request):
    """
    This function handles user login by authenticating the user's credentials and returning a JWT token.

    """
    # Get the parameters from the request object
    data = request.data
    person = request.person
    session = request.session

    refresh_token = generate_new_refresh_token(person, session).get('token')

    # Return a success response
    response = JsonResponse({
        "answer": "Logout successfuly.",
        'person': '',
        "access_token": '',
        "refresh_token": ''}, status=200)

    response.set_cookie('person_id', '')
    response.set_cookie('access_token', '')
    response.set_cookie('refresh_token', '')

    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def change_password(request):

    data = request.data
    person = request.person

    confirm_new_password = data.get('confirm_new_password')
    new_password = data.get('new_password')
    current_password = data.get('current_password')

    if not person.verify_password(current_password):
        # If password is incorrect, return an error response
        response = JsonResponse(
            {'answer': "Invalid current_password password."}, status=401)

        add_get_params(response)
        return response

    # Validate the new password meets the required complexity criteria
    if not is_valid_password(new_password):
        response = JsonResponse(
            {"error": "The new password does not meet the required complexity criteria."},
            status=400
        )

        add_get_params(response)
        return response

    if confirm_new_password != new_password:
        response = JsonResponse(
            {"error": "The new password does not meet the confirm new password."},
            status=400
        )

        add_get_params(response)
        return response

    # Change user password
    person.hash_password(new_password)

    reset_link = request.build_absolute_uri(
        f'/send_password_reset_link/?email={person.email}'
    )

    body_html_message_with_token = create_html_message_with_token(token_with_url=reset_link,
                                                                  header_text='Your password has changed',
                                                                  header_details_text="Your password has changed. Get password reset link if you haven't.",
                                                                  link_text="Send me the password reset link")

    send_email(person.email, "Your password has changed.",
               body_html_message_with_token)

    # Generate new access and refresh tokens for the user
    refresh_token = generate_new_refresh_token(
        person, request.session).get('token')
    access_token = generate_new_access_token(person.id).get('token')

    # Create a response object with the new access and refresh tokens
    response = JsonResponse(
        {
            "answer": "Password reset successful.",
            "person": person.to_json(),
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        status=200
    )

    # Set cookies for the new tokens in the response
    response.set_cookie('person_id', person.id)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)

    # Add GET parameters to the response for easier debugging
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_person(request):
    """
    Update an existing user in the database.

    Args:
        request: HttpRequest object representing the current request.

    Request Parameters:
        user_name (str): The username of the user to be updated.
        new_values (dict): A dictionary of the new values for the user. The keys in the dictionary should correspond to the names of the columns in the 'users' table, and the values should be the new values for each column.

    Returns:
        JsonResponse: A JSON response indicating whether the update was successful.

    Raises:
        ValueError: If the required request parameters are missing or invalid.
        PermissionDenied: If the requesting user does not have permission to update the specified user.
    """

    # Extract required parameters from the request
    data = request.data  # get the data from the request
    session = request.session  # get the session from the request
    person = request.person  # get the person object from the request
    new_values = data.get('new_values')  # get the new_values from the data

    # Check that required parameters are present and valid
    if not new_values:  # check if new_values are missing
        response = JsonResponse(
            {'answer': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response

    # Check if any of the disallowed columns are being updated
    # Update user object with new values
    not_allowed_column = ['id', 'active', 'phone_verify', 'phone_number_id', 'location_id', 'person_type', '_password',
                          'password', 'token', 'refresh_token_id']  # set of columns that cannot be updated through this endpoint
    check_change_email = False  # initialize flag for email change
    old_email = person.email  # get old email of person
    # iterate through new_values
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():  # iterate through the columns in the new_value
            if column_name in not_allowed_column:  # check if the column is disallowed
                response = JsonResponse(
                    {'answer': f"Cannot update {column_name} through this endpoint."}, status=400)
                add_get_params(response)
                return response

            if column_name == "email":  # check if email is being updated
                check_change_email = True

            print(f"{column_name}:{value}")
            # set the new value of the column in the person object
            setattr(person, column_name, value)

    """Handle special case where email is being updated"""

    if check_change_email:     # if email is being updated
        return email_replacement_process(person, old_email)
    # Handle case where email is not being updated

    response = JsonResponse(
        {'Success': 'The person has been successfully updated'}, status=200)
    add_get_params(response)
    return response


def email_replacement_process(person, old_email):
    header_text = 'Your Delta E-commerce account email has been changed.'
    header_details_text = f'Your Delta E-commerce account email has been changed from {old_email} to {person.email}. If you did not do this, please ensure the security. Get your account back.'
    link_text = 'Get account back!'
    extra_variables = f'&email={old_email}'

    person_id = person.id
    reset_token = generate_new_access_token(
        person_id, minutes=1440).get('token')

    token_with_url = f'{str(HOST_URL)}/give_reset_password_permission/?reset_token={reset_token}{extra_variables}'

    body_html_message_with_token = create_html_message_with_token(token_with_url=token_with_url,
                                                                  header_text=header_text,
                                                                  header_details_text=header_details_text,
                                                                  link_text=link_text)

    send_email(old_email, "Your email has been changed",
               body_html_message_with_token)
    person.active = False

    send_verification_code(person_id, person.email)
    print(
        f"Your email changed from {old_email} to {person.email}. Please verify your new email.")
    response = JsonResponse(
        {
            'answer': 'The person has been successfully updated',
            'about_email': f"Your email changed from {old_email} to {person.email}. Please verify your new email."
        }, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "GET"])
def send_password_reset_link(request):
    """
    POST request to send a password reset link to a user's email address.
    The function receives the following parameters from the request object:
    - email: the email address of the user whose password is being reset

    If the email address is valid and associated with an existing account, the function generates a unique token with a limited lifespan and sends an email to the user with a link to reset their password.
    If an error occurs during the token generation or email sending process, the function returns a JSON response with an error message and the error details.
    """

    # Get the email address from the request object
    data = request.data
    email = data.get('email')
    session = request.session

    # Query for the user object associated with the email address
    person = session.query(Person).filter_by(email=email).one_or_none()

    if not person:
        # If user is not found, return an error response
        response = JsonResponse(
            {'answer': "No user account associated with this email address."}, status=400)

        add_get_params(response)
        return response

    # Construct the password reset link
    reset_token = generate_new_access_token(
        person.id, minutes=1440).get('token')
    reset_link = request.build_absolute_uri(
        f'/give_reset_password_permission/?reset_token={reset_token}'
    )

    # Send the password reset link to the user's email
    send_email(
        email,
        'Password reset link',
        f'Please use the following link to reset your password: {reset_link}',
    )

    # Indicate that the email was sent successfully
    # logger.info(f"Password reset link has been sent to {email}.")

    # Return a success response
    response = JsonResponse(
        {"success": "A password reset link has been sent to your email account. Please check your email and follow the instructions.",
            "email": email},
        status=200
    )
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "GET"])
def give_reset_password_permission(request):
    """
    This function handles giving permission to reset a user's password by verifying the reset token.
    The function receives the following parameters from the request object:
    - reset_token: the JWT token received by the user in the password reset email

    If the reset token is valid and has not expired, the function generates and returns a new access token and refresh token for the user's account.
    If an error occurs during the token decoding process, the function returns a JSON response with an error message and the error details.
    """

    try:
        # Get the reset token from the request data
        data = request.data
        reset_token = data.get('reset_token')
        email = data.get('email')
        # Start a new database session
        session = request.session

        # Decode the reset token to extract the person ID
        decoded_token = jwt.decode(
            reset_token, SECRET_KEY, algorithms=["HS256"])
        person_id = decoded_token.get('person_id')

        # Query for the user object associated with the person ID
        person = session.query(Person).get(person_id)

        # If user is not found, return an error response
        if not person:
            response = JsonResponse(
                {'answer': "No person account associated with this username."}, status=400)
            add_get_params(response)
            return response

        if email:
            person.email = email

        # Generate new access and refresh tokens for the user
        refresh_token = generate_new_refresh_token(
            person, session).get('token')
        access_token = generate_new_access_token(person.id).get('token')

        # Return the access token and the refresh token in the response
        response = JsonResponse({"answer": "Input new password.",
                                "access_token": access_token, "refresh_token": refresh_token}, status=200)

        # Set the access and refresh tokens as cookies in the response
        response.set_cookie('person_id', person.id)
        response.set_cookie('access_token', access_token)
        response.set_cookie('refresh_token', refresh_token)

        # Add any GET parameters to the response
        add_get_params(response)
        return response

    except Exception as e:
        # Return an error response if there was an error decoding the reset token
        response = JsonResponse(
            {"error": "Something went wrong when resetting your password.", "details": str(e)}, status=400)
        add_get_params(response)
        return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def reset_password(request):
    """
    Handles resetting a user's password.

    Receives the following parameters from the request object:
    - new_password: the new password to set for the user's account
    - confirm_new_password: the confirmation of the new password

    If the new password meets the required complexity criteria, the function updates the user's password in the database.
    If an error occurs during the password updating process, the function returns a JSON response with an error message and the error details.
    """

    # Get the new password and its confirmation from the request object
    data = request.data
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    # Get the user object associated with the request

    # Update the user's password in the database

    person = request.person

    # Validate the new password meets the required complexity criteria
    if not is_valid_password(new_password):
        response = JsonResponse(
            {"error": "The new password does not meet the required complexity criteria."},
            status=400
        )

        add_get_params(response)
        return response

    # Validate the new password matches its confirmation
    if new_password != confirm_new_password:
        response = JsonResponse(
            {"error": "The new password is not the same as the confirmation password."},
            status=400
        )

        add_get_params(response)
        return response

    person.hash_password(new_password)

    send_email(person.email, "Your password has changed.",
               "Your new password has been successfully reset.")

    # Generate new access and refresh tokens for the user
    refresh_token = generate_new_refresh_token(
        person, request.session).get('token')
    access_token = generate_new_access_token(person.id).get('token')

    # Create a response object with the new access and refresh tokens
    response = JsonResponse(
        {
            "answer": "Password reset successful.",
            "person": person.to_json(),
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        status=200
    )

    # Set cookies for the new tokens in the response
    response.set_cookie('person_id', person.id)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)

    # Add GET parameters to the response for easier debugging
    add_get_params(response)

    return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage persons")
def change_null_password(request):
    # Start a database session
    session = request.session

    # Select all rows where username is empty
    empty_usernames = session.query(Person).filter(Person._password is None).all()

    # Generate random word as new username
    for empty_username in empty_usernames:
        empty_username.hash_password("Farid612")
    # Commit changes

    response = JsonResponse(
        {'message': "Change null password process succesfully completed"})
    add_get_params(response)
    return response
