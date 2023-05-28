from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, permission_required, require_http_methods
from DjApp.models import Category, Product, Supplier


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_all_suppliers(request):
    """
    This function retrieves all suppliers from the database and returns them as a JSON response.
    """
    session = request.session

    # Query for all suppliers in the database
    suppliers = session.query(Supplier).all()

    # Convert each supplier object to JSON format
    suppliers_json = [supplier.to_json() for supplier in suppliers]

    return JsonResponse({"suppliers": suppliers_json}, status=200)


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_all_products_by_supplier(request, supplier_id):
    """
    This function returns all products that belong to a supplier by given supplier name.
    The supplier name is passed as a query parameter in the GET request.
    If the supplier does not exist, it returns a JSON response with an 'Is empty' message.
    If the supplier_name parameter is not provided in the GET request, it returns a JSON response with an 'answer' message.
    """
    # Get the supplier name from the GET request
    data = request.data
    session = request.session

    # Check if the supplier_name parameter was provided in the GET request
    if not supplier_id:
        return JsonResponse(
            {'answer': 'supplier_id is not a required parameter'}, status=400
        )
    supplier = session.query(Supplier).get(supplier_id)
    if not supplier:
        return JsonResponse({'answer': 'Supplier does not exist'}, status=400)
    all_products = session.query(Product).filter_by(
        supplier_id=supplier_id).order_by(Category.id)

    products_data = [product.to_json() for product in all_products]
    return JsonResponse(
        {f'{supplier.name} products': products_data}, status=200
    )
