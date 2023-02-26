import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import CardItem, ShoppingSession, UserPayment
from ..helpers import GetErrorDetails, add_get_params, session_scope
from ..decorators import login_required, require_http_methods



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_user_payment(request):
    """
    This function handles adding payment information for a user.
    The function receives the following parameters from the request object:
    - payment_type: the type of payment (e.g. "Credit Card", "Paypal")
    - provider: the payment provider (e.g. "VISA", "Mastercard")
    - account_no: the account number of the user
    - expiry: the expiry date of the user's payment information

    If the payment information is added successfully, the function returns a JSON response with a success message.
    If an error occurs during the process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Start a new database session

        # Get the parameters from the request object
        data = request.data
        session = request.session
        payment_type = data.get('payment_type')
        provider = data.get('provider')
        account_no = data.get('account_no')
        expiry = data.get('expiry')


        user_id = request.user.id
        # Create a new user payment object with the given parameters
    
        new_payment = UserPayment(user_id=user_id,
                                payment_type=payment_type,
                                provider=provider,
                                account_no=account_no,
                                expiry=expiry)

        # Add the new payment information to the database and commit the changes
        session.add(new_payment)
    
        # Return a JSON response with a success message
        response = JsonResponse({"Success": "The payment information has been successfully added."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding payment information.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_user_payment(request):
    """
    This function updates the payment information for a user with the given user ID.
    The function receives the following parameters from the request object:
    - payment_type: the updated payment type (e.g. credit card, debit card, etc.)
    - provider: the updated payment provider (e.g. Visa, Mastercard, etc.)
    - account_no: the updated account number
    - expiry: the updated expiry date of the payment method

    If the update is successful, the function returns a JSON response with a success message and the updated user payment information.
    If an error occurs during the update process, the function returns a JSON response with an error message and the error details.
    """
    try:


        # Get the parameters from the request object
        data = request.data
        session = request.session
        
        payment_type = data.get('payment_type')
        provider = data.get('provider')
        account_no = data.get('account_no')
        expiry = data.get('expiry')

        user_id = request.user.id
        # Query the database for the user with the given ID
        
        user_payment = session.query(UserPayment).filter_by(user_id=user_id).first()

        # Update the payment information for the user
        user_payment.payment_type = payment_type
        user_payment.provider = provider
        user_payment.account_no = account_no
        user_payment.expiry = expiry

        # Return a JSON response with a success message and the updated user payment information
        response = JsonResponse({"Success":"The payment information has been successfully updated.","user_id": user_id, "payment_type": payment_type, "provider": provider, "account_no": account_no, "expiry": expiry}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when updating the payment information.", e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_user_payment(request):
    """
    This function deletes a user payment from the database.
    The function receives the following parameters from the request object:
    - id: the id of the user payment to be deleted

    If the deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Start a new database session

        # Get the user payment with the specified id
        user_id = request.user.id
        session = request.session
        
        # Query the database for the user with the given ID
    
        user_payment = session.query(UserPayment).filter_by(user_id=user_id).first()

        # Check if the user payment exists
        if user_payment is None:
            raise Exception("User payment not found.")

        # Delete the user payment from the database and commit the changes
        session.delete(user_payment)


        # Return a JSON response with a success message
        response = JsonResponse({"Success":"The user payment has been successfully deleted."}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when deleting user payment.", e, 500)
        add_get_params(response)
        return response


