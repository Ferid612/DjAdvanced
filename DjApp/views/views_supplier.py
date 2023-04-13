from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, permission_required, require_http_methods
from DjApp.helpers import add_get_params
from DjApp.models import ProfilImage, Supplier


@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
# @login_required
# @permission_required('manage_supplier')
def get_all_suppliers(request):
    """
    This function retrieves all suppliers from the database and returns them as a JSON response.
    """
    session = request.session

    # Query for all suppliers in the database
    suppliers = session.query(Supplier).all()

    # Convert each supplier object to JSON format
    suppliers_json = [supplier.to_json() for supplier in suppliers]

    # Return a success response with the list of suppliers
    response = JsonResponse(
        {"suppliers": suppliers_json},
        status=200
    )

    return response


