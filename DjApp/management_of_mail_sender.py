from django.core.mail import send_mail
from django.http import JsonResponse
import datetime 
import jwt
from DjAdvanced.settings import EMAIL_HOST_USER, SECRET_KEY,HOST_URL
from DjApp.decorators import login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope 
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
# from DjApp.models import Users
from django.core.mail import send_mail


def send_email(usermail, subject, body):
    """
    Function to send an email to the provided email address.
    :param usermail: email address to send the email to
    :param subject: subject of the email
    :param body: body of the email
    :return: None
    """
    # sender email address
    sender_email = EMAIL_HOST_USER

    try:
        # send the email
        send_mail(subject, body, sender_email, [usermail], html_message=body)
    except Exception as e:
        # in case of an error, print the error message
        response = JsonResponse({"message":"something went wrong when sending mail"}, status=400)
        add_get_params(response)
        return response
    print("message", "Mail succesfully sending")



@csrf_exempt
def send_verification_code(request,token):
    """
    Sends a verification email to the user with a link to verify their account.

    @param request: The request object that contains the username and email of the user.
    @param token: The token that will be used for account verification.

    @return: A JSON response indicating whether the email was successfully sent or not.
    """
    try:
        # Get the username and email from the request object 
        data = request.data
        username = data.get('username')
        usermail = data.get('usermail')

        # Create the link to verify the account using the token and username 
        token_with_url = HOST_URL + "/get_verification/?token=" + token + "&username=" + username

        # Create the HTML message body 
        body_html_message = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verification Token</title>
                <style>
                   /* Add your custom styles here */
            body {
                font-family: Arial, sans-serif;
                color: #333;
            }
            .container {
                max-width: 500px;
                margin: 0 auto;
                text-align: center;
                padding: 30px;
                background-color: #f0f0f0;
                border-radius: 10px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }
            h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #3399ff;
                color: #fff;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
                </style>
            </head>
            <body>
                <div class="container">
                <h1>Verification Token</h1>
                <p>Your verification code:</p>
                <a class="btn" href="""+ token_with_url+""">Verificate!</a>
                </div>
            </body>
            </html>
                """

        # Send the email to the user 
        send_email(usermail, "Verification Token", body_html_message)

        # Return a JSON response indicating the email was sent successfully 
        response = JsonResponse({"Success":"The new token has been successfully sended. Please check your email account. And verify your account."}, status=200)
        return response
    except Exception as e:
        # If there was an error sending the email, return the error details 
        response = GetErrorDetails("Something went wrong when sending verification code.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_verification_code_after_login(request):
    """
    Sends a verification email to the user with a link to verify their account.

    @param request: The request object that contains the username and email of the user.
    @param token: The token that will be used for account verification.

    @return: A JSON response indicating whether the email was successfully sent or not.
    """
    try:
        # Get the username and email from the request object 
        data = request.data
        username = data.get('username')
        usermail = data.get('usermail')


        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        token = jwt.encode({"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")
    
        # Create the link to verify the account using the token and username 
        token_with_url = HOST_URL + "/get_verification/?token=" + token + "&username=" + username

        # Create the HTML message body 
        body_html_message = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verification Token</title>
                <style>
                   /* Add your custom styles here */
            body {
                font-family: Arial, sans-serif;
                color: #333;
            }
            .container {
                max-width: 500px;
                margin: 0 auto;
                text-align: center;
                padding: 30px;
                background-color: #f0f0f0;
                border-radius: 10px;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            }
            h1 {
                font-size: 24px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #3399ff;
                color: #fff;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
                </style>
            </head>
            <body>
                <div class="container">
                <h1>Verification Token</h1>
                <p>Your verification code:</p>
                <a class="btn" href="""+ token_with_url+""">Verificate!</a>
                </div>
            </body>
            </html>
                """

        # Send the email to the user 
        send_email(usermail, "Verification Token", body_html_message)

        # Return a JSON response indicating the email was sent successfully 
        response = JsonResponse({"Success":"The new token has been successfully sended. Please check your email account. And verify your account."}, status=200)
        return response

    except Exception as e:
        # If there was an error sending the email, return the error details 
        response = GetErrorDetails("Something went wrong when sending verification code.", e, 500)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def verify_account(request):
    try:
        # decode the token to retrieve the user's id


        with session_scope() as session:

            # query the user with the id
            person = request.person
            person.active = True

        # db.session.commit()
        response = JsonResponse({"answer":"True","message":"Your account has been verified. Please log in to continue.",},status=200)
        add_get_params(response)
        return response

    except jwt.ExpiredSignatureError:
        response =  JsonResponse({"answer":"False",'Error':'The verification link has expired. Please register again.',},status=400)
        add_get_params(response)        
        return response
    
    except jwt.InvalidTokenError:
        response =  JsonResponse({"answer":"False",'Error':'Invalid token.'},status=400)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
def contact_us(request):
    """
    A view function that allows a user to send an email through the contact us form.
    Parameters:
        request (HttpRequest): A Django HttpRequest object containing the POST data from the form.
    Returns:
        JsonResponse: A JSON response indicating whether the email was sent successfully or not.
    """
    
    try:
        # Get the form data from the request object
        data = request.data
        full_name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        # Compose the subject and message
        subject = f"From contact us. Sender: {full_name} Sender email: {email} Subject: {subject}"
        message = f"Quest message: {message}"
        
        # Call the send_email function
        send_email(EMAIL_HOST_USER, subject, message)
        
    except Exception as e:
        # Catch and log any exceptions that occur during email sending
        response = JsonResponse({"message":"something went wrong when sending mail"}, status=400)
        add_get_params(response)
        return response
            
    # Return a JSON response indicating success
    response = JsonResponse({"message": "Mail successfully sent"}, status=200)
    add_get_params(response)
    return response
