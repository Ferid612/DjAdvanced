from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, require_http_methods
from ..models import ProductEntry, UserWishList, WishList, WishListProductEntry
from ..helpers import  add_get_params




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_wishlist(request):
    """
    This function handles the creation of a new wishlist for a user.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user for which the wishlist should be created
    - title: the title of the wishlist to be created
    If the wishlist creation is successful, the function returns a JSON response with a success message and the new wishlist's information.
    If an error occurs during the wishlist creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    title = request.data.get("title")
    user = request.person.user[0]
    session = request.session

    if not (user or title):
        response = JsonResponse({'answer': 'False', 'message': 'Missing data error. User ID and Title must be filled.'}, status=404)
        add_get_params(response)
        return response
    

    if not user:
        response = JsonResponse({'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    # Check if the user already has a wishlist
    user_wishlist = session.query(UserWishList).filter_by(user_id=user.id).first()
    
    if not user_wishlist:
            
        # Create a new wishlist object with the given parameters
        new_user_wishlist = UserWishList(
            user_id=user.id,
        )    
        # Add the new wishlist to the database and commit the changes
        session.add(new_user_wishlist)
        session.commit()
        user_wishlist = new_user_wishlist
    
    
    new_wishlist = WishList(
            user_wishlist_id=user_wishlist.id,
            title=title
        )    
        # Add the new wishlist to the database and commit the changes
       
    session.add(new_wishlist)
    session.commit()

    
    # Return a JSON response with a success message and the new wishlist's information
    response = JsonResponse({'Success': 'The new wishlist has been successfully created.',"new_wishlist_id":new_wishlist.id ,'user_id': user.id, 'title': title}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
@login_required
def update_wishlist_title(request, wishlist_id):
    """
    This function handles the updating of a wishlist's title for a user.
    The function receives the following parameters from the request object:
    - wishlist_id: the ID of the wishlist to be updated
    - title: the new title of the wishlist
    If the wishlist update is successful, the function returns a JSON response with a success message and the updated wishlist's information.
    If an error occurs during the wishlist update process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    title = request.data.get("title")
    user = request.person.user[0]
    session = request.session

    if not (wishlist_id or title):
        response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Wishlist ID and Title must be filled.'}, status=404)
        add_get_params(response)
        return response
    
    if not user:
        response = JsonResponse({'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).get(wishlist_id)
    
    if not wishlist:
        response = JsonResponse({'answer': 'False', 'message': 'Wishlist with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    
    if wishlist.user_wishlist.user_id != user.id:
        response = JsonResponse({'answer': 'False','message': 'Wishlist with the given ID does not belong to the user.'}, status=404)
        add_get_params(response)
        return response
    
    
    # Update the wishlist title with the new title parameter
    wishlist.title = title
    session.commit()

    # Return a JSON response with a success message and the updated wishlist's information
    response = JsonResponse({'Success': 'The wishlist title has been successfully updated.',"wishlist_id":wishlist.id ,'user_id': user[0].id, 'title': wishlist.title}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
@login_required
def delete_wishlist(request, wishlist_id):
    """
    This function handles the deleting of a wishlist for a user.
    The function receives the following parameters from the request object:
    - wishlist_id: the ID of the wishlist to be deleted
    If the wishlist deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the wishlist deletion process, the function returns a JSON response with an error message and the error details.
    """

    # Get the user from the request object
    user = request.person.user[0]
    session = request.session

    if not wishlist_id:
        response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Wishlist ID must be filled.'}, status=404)
        add_get_params(response)
        return response
    
    if not user:
        response = JsonResponse({'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).get(wishlist_id)
    if not wishlist:
        response = JsonResponse({'answer': 'False', 'message': 'Wishlist with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    
    if wishlist.user_wishlist.user_id != user.id:
        response = JsonResponse({'answer': 'False','message': 'Wishlist with the given ID does not belong to the user.'}, status=404)
        add_get_params(response)
        return response
    
    # Delete the wishlist
    session.delete(wishlist)
    session.commit()

    # Return a JSON response with a success message
    response = JsonResponse({'Success': 'The wishlist has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_product_entry_to_wishlist(request):
    """
    This function adds a product entry to a wishlist with the given wishlist_id.
    The function receives the following parameters from the request object:
    - wishlist_id: the ID of the wishlist to which the product entry should be added
    - product_entry_id: the ID of the product entry to be added to the wishlist
    If the product entry is successfully added to the wishlist, the function returns a JSON response with a success message.
    If an error occurs during the product entry addition process, the function returns a JSON response with an error message and the error details.
    """
    
    session = request.session
    user = request.person.user[0]

    # Get the parameters from the request object
    wishlist_id = request.data.get("wishlist_id")
    product_entry_id = request.data.get("product_entry_id")

    # Check if both wishlist_id and product_entry_id are provided
    if not (wishlist_id and product_entry_id):
        response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Wishlist ID and Product Entry ID must be filled.'}, status=404)
        add_get_params(response)
        return response

    # Retrieve the wishlist with the given wishlist_id
    wishlist = session.query(WishList).get(wishlist_id)

    # If the wishlist does not exist, return an error message
    if not wishlist:
        response = JsonResponse({'answer': 'False', 'message': 'Wishlist with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response

    # Check if the user is the owner of the wishlist
    if wishlist.user_wishlist.user_id != user.id:
        response = JsonResponse({'answer': 'False', 'message': 'You are not authorized to add products to this wishlist.'}, status=401)
        add_get_params(response)
        return response

    # Retrieve the product entry with the given product_entry_id
    product_entry = session.query(ProductEntry).get(product_entry_id)

    # If the product entry does not exist, return an error message
    if not product_entry:
        response = JsonResponse({'answer': 'False', 'message': 'Product entry with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response

    # Check if the product entry is already in the wishlist
    if product_entry in wishlist.product_entries:
        response = JsonResponse({'answer': 'False', 'message': 'Product entry is already in the wishlist.'}, status=400)
        add_get_params(response)
        return response

    # Create a new WishListProductEntry object and add it to the wishlist's product_entries list
    wishlist_product_entry = WishListProductEntry(wishlist_id=wishlist_id, product_entry_id=product_entry_id)

    # Add the changes to the database
    session.add(wishlist_product_entry)

    # Commit the changes to the database
    session.commit()

    # Return a JSON response with a success message
    response = JsonResponse({'Success': 'Product entry has been successfully added to the wishlist.'}, status=200)
    add_get_params(response)
    return response
