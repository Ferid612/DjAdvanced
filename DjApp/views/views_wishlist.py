from django.http import JsonResponse
from sqlalchemy.orm import joinedload
from DjApp.models import WishList
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import login_required, require_http_methods
from ..helpers import  add_get_params



@csrf_exempt
@require_http_methods(["GET","POST","OPTIONS"])
@login_required
def get_user_wishlists_list(request,count=None):
    """
    This function handles the retrieval of all the wishlists associated with a user.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user for which to retrieve the wishlists
    If the retrieval is successful, the function returns a JSON response with a success message and the wishlists' information.
    If an error occurs during the retrieval process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    user = request.person.user[0]
    session = request.session


    if not user:
        response = JsonResponse({'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    wishlists = user.get_user_wishlists_list(count)
    
    # Return a JSON response with a success message and the wishlists' information
    response = JsonResponse({'Success': 'The user wishlists have been successfully retrieved.','user_id':user.id, "wishlists":wishlists }, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["GET","POST","OPTIONS"])
@login_required
def get_user_wishlist(request,wishlist_id):
    """
    This function handles the retrieval of all the wishlists associated with a user.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user for which to retrieve the wishlists
    If the retrieval is successful, the function returns a JSON response with a success message and the wishlists' information.
    If an error occurs during the retrieval process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    user = request.person.user[0]
    session = request.session

    if not user:
        response = JsonResponse({'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    wishlist = session.query(WishList).filter_by(id=wishlist_id, user_id=user.id).first()
    if not wishlist:
        response = JsonResponse({'answer': 'False','message': 'Wishlist with given ID does not exist in this user'}, status=404)
        add_get_params(response)
        return response
    
    
    wishlist_data = wishlist.to_json()
    
    
    # Return a JSON response with a success message and the wishlists' information
    response = JsonResponse({'Success': 'The user wishlists have been successfully retrieved.','user_id':user.id, "wishlists":wishlist_data }, status=200)
    add_get_params(response)
    return response






