from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, permission_required, require_http_methods
from DjApp.helpers import add_get_params
from DjApp.models import ProfilImage, Supplier


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required('manage_supplier')
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



@csrf_exempt
@require_http_methods(["GET","POST"])
def get_suppplier_profil_image(request):
    data = request.data
    session = request.session
    supplier_id = data.get("supplier_id")
    
    # Query for the supplier_id object
    supplier = session.query(Supplier).get(supplier_id)
    if not supplier:
        # If supplier_id is not found, return an error response
        response = JsonResponse(
            {'error': "Invalid supplier id."}, status=401)
        return response

    
    profil_image = session.query(ProfilImage).filter_by(supplier_id=supplier_id).one_or_none()
    
    if not profil_image:
            # If supplier_id is not found, return an error response
        response = JsonResponse(
            {'error': "Profil image don't exist."}, status=501)
        return response

    
    # Return a success response
    response = JsonResponse(
        {"profil_image": profil_image.to_json()},
        status=200
    )
    add_get_params(response)
    return response
