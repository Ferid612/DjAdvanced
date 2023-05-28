from sqlalchemy import or_
from ..models import Product
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import require_http_methods
from django.http import JsonResponse

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def search_product(request):
    # Get the search query from the request parameters
    search_query = request.GET.get('q', 'red')

    # Get the SQLAlchemy session from the request object
    session = request.session

    # Perform the search query using ilike for case-insensitive pattern matching
    result = session.query(Product).filter(or_(Product.name.ilike(f'%{search_query}%'),
                                                Product.description.ilike(f'%{search_query}%'))).all()

    # Convert the result to JSON-compatible dictionaries
    result_data = [product.to_json() for product in result]

    # Return a JSON response containing the search result
    return JsonResponse({
        'result': result_data
    }, status=200)