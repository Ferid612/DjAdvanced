from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, token_required
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
# from .models import Users



@csrf_exempt
@token_required
def get_user_data_by_username(request):
    """
    API endpoint to retrieve user information by username.
    The user data includes the following fields:
    - id
    - username
    - usermail
    - first_name
    - last_name
    - telephone
    - created_at
    - modified_at
    - active
    - phone_verify
    """
    try:
        # Get the user object associated with the request
        user = request.user

        # Build the user data dictionary
        user_data = {
            "id": user.id,
            "username": user.username,
            "usermail": user.usermail,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "telephone": user.telephone,
            "created_at": user.created_at,
            "modified_at": user.modified_at,
            "active": user.active,
            "phone_verify": user.phone_verify
        }

        # Return a JSON response with the user data
        response = JsonResponse(user_data, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details if an exception occurs
        response = GetErrorDetails("An error occurred while getting user information.", e, 500)
        add_get_params(response)
        return response
