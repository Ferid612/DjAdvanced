from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required,require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
# from .models import Users



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("")
def get_person_data_by_username(request):
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
        person = request.person

        # Build the user data dictionary
        user_data = {
            "id": person.id,
            "username":person.username,
            "usermail":person.email,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "phone_number_id": person.phone_number_id,
            "location_id": person.location_id,
            "created_at": person.created_at,
            "modified_at": person.updated_at,
            "active": person.active,
            "phone_verify": person.phone_verify,
            "person_type": person.person_type
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
