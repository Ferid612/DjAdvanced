from ..models import Product
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import require_http_methods

@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def search_product(request):
    # Get the product from the database
    session = request.session
    results = session.query(Product).filter(Product.name.match('Red')).all()
    print(results)

    
