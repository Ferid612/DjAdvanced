from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..decorators import login_required, require_http_methods


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_shopping_session(request):
    """
    Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
    """
    try:
        session = request.session
        shopping_session = request.person.user.shopping_session[0]
    except Exception:
        return JsonResponse({'answer': "The session data of the user could not be found. Please add any product to basket. After remove it."}, status=400)

    if not shopping_session:
        return JsonResponse({'answer': "The session data of the user could not be found."}, status=400)

    response_data = shopping_session.get_user_shopping_session_data(session)
    return JsonResponse(response_data)



@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_orders(request):
    """
    Retrieves all the orders for the authenticated user along with the corresponding product data.
    
    Args:
        request: HttpRequest object representing the current request.
        
    Returns:
        JsonResponse: JSON response containing the order history for the user.
    """
    user = request.person.user
    orders = user.orders
    
    status = request.data.get('status')

    if status is not None:
        print(status)
        orders = [order for order in orders if order.status == status]

    if not orders:
        return JsonResponse({'error': "No orders found for the user."}, status=400)

    order_dicts = [order.to_json() for order in orders]

    return JsonResponse({
        'message': 'Order history successfully retrieved.',
        'orders': order_dicts
    }, status=200)



@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_cart_item_count(request):
    """
    Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
    """
    shopping_session = request.person.user.shopping_session[0]

    if not shopping_session:
        return JsonResponse({'answer': "The session data of the user could not be found."}, status=400)

    response_data = {
        "cart_item_count": shopping_session.get_count_of_cart_items()}
    return JsonResponse(response_data, status=200)
