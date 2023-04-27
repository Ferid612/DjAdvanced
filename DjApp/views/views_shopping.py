import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import CartItem,   ProductEntry,  ShoppingSession
from ..helpers import  add_get_params
from ..decorators import login_required, require_http_methods
from sqlalchemy.orm import joinedload


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_user_shopping_session_data(request):
    """
    Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
    """
    shopping_session = request.person.user[0].shopping_session[0]

    if not shopping_session:
        return JsonResponse({'answer': "The session data of the user could not be found."}, status=400)


    response_data = shopping_session.get_user_shopping_session_data()
    response = JsonResponse(response_data)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_cart_item_count(request):
    """
    Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
    """
    shopping_session = request.person.user[0].shopping_session[0]

    if not shopping_session:
        return JsonResponse({'answer': "The session data of the user could not be found."}, status=400)



    response_data = {"cart_item_count":shopping_session.get_count_of_cart_items()}
    response = JsonResponse(response_data,status=200)
    add_get_params(response)
    return response


