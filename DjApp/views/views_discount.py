from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, permission_required, require_http_methods
from DjApp.helpers import add_get_params
from DjApp.models import Discount



@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
@permission_required("manage_discounts")
def get_all_discounts(request):
    """
    Retrieve all discounts from the database.

    Args:
        request: HttpRequest object representing the current request.

    Returns:
        JsonResponse: A JSON response containing a list of all discounts.
    """

    session = request.session

    discounts = session.query(Discount).all()

    discounts_json = [discount.to_json() for discount in discounts]

    response = JsonResponse(discounts_json, safe=False)
    add_get_params(response)
    return response
