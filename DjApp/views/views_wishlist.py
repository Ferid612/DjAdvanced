from django.http import JsonResponse
from sqlalchemy.orm import joinedload
from DjApp.models import UserWishList, WishList
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import login_required, require_http_methods
from ..helpers import  add_get_params



def get_user_wishlists(session,user_id):
    """
    This function retrieves all the wishlists associated with the user's id provided as a parameter.
    It returns a list of dictionaries, each containing the wishlist's information.
    """
    user_wishlist = session.query(UserWishList).options(joinedload(UserWishList.wishlists)).filter_by(user_id=user_id).first()

    if user_wishlist:
        wishlists = user_wishlist.wishlists
        return [wishlist.to_json() for wishlist in wishlists]
    else:
        return []






@csrf_exempt
@require_http_methods(["GET","POST","OPTIONS"])
@login_required
def get_user_wishlists_view(request):
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
    
    wishlists = get_user_wishlists(session ,user.id)
    
    # Return a JSON response with a success message and the wishlists' information
    response = JsonResponse({'Success': 'The user wishlists have been successfully retrieved.',"wishlists":wishlists }, status=200)
    add_get_params(response)
    return response
