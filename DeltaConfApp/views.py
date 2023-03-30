from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required,require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params


# Create your views here.
@csrf_exempt
@require_http_methods(["POST","GET","OPTIONS"])
def get_home_swipers(request):
    try:
        # Get the user object associated with the request
        json_data = {"data":"value"}
        # Build the user data dictionary

        # Return a JSON response with the user data
        response = JsonResponse(json_data, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details if an exception occurs
        response = GetErrorDetails("An error occurred while getting user information.", e, 500)
        add_get_params(response)
        return response