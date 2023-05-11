from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sqlalchemy.exc import SQLAlchemyError
from DjApp.decorators import login_required, require_http_methods
from ..models import ProductEntry, WishList, WishListProductEntry
from ..helpers import add_get_params


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
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. User ID and Title must be filled.'}, status=404)
        add_get_params(response)
        return response

    # check user is exist 
    if (
        session.query(WishList)
        .filter_by(user_id=user.id, title=title)
        .first()
    ):
        response = JsonResponse(
            {'answer': 'False', 'message': 'The user already has a wishlist with this title.'}, status=404)
        add_get_params(response)
        return response

    # Add the new wishlist to the database and commit the changes
    new_wishlist = WishList(
        user_id=user.id,
        title=title
    )

    session.add(new_wishlist)
    session.commit()

    # Return a JSON response with a success message and the new wishlist's information
    response = JsonResponse({'Success': 'The new wishlist has been successfully created.',
                            "wishlist": new_wishlist.to_json()}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
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
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. Wishlist ID and Title must be filled.'}, status=404)
        add_get_params(response)
        return response

    if not user:
        response = JsonResponse(
            {'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response

    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).filter_by(
        id=wishlist_id, user_id=user.id).first()
    if not wishlist:
        response = JsonResponse(
            {'answer': 'False', 'message': 'The user does not have a wishlist with this ID.'}, status=404)
        add_get_params(response)
        return response

    # Update the wishlist title with the new title parameter
    wishlist.title = title
    session.commit()

    # Return a JSON response with a success message and the updated wishlist's information
    response = JsonResponse({'Success': 'The wishlist title has been successfully updated.',
                            "wishlist_id": wishlist.id, 'user_id': user[0].id, 'title': wishlist.title}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
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
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. Wishlist ID must be filled.'}, status=404)
        add_get_params(response)
        return response

    if not user:
        response = JsonResponse(
            {'answer': 'False', 'message': 'User with the given ID does not exist.'}, status=404)
        add_get_params(response)
        return response

    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).filter_by(
        id=wishlist_id, user_id=user.id).first()
    if not wishlist:
        response = JsonResponse(
            {'answer': 'False', 'message': 'The user does not have a wishlist with this ID.'}, status=404)
        add_get_params(response)
        return response

    # Delete the wishlist
    session.delete(wishlist)
    session.commit()

    # Return a JSON response with a success message
    response = JsonResponse(
        {'Success': 'The wishlist has been successfully deleted.'}, status=200)
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
    product_entry_id = int(request.data.get("product_entry_id"))

    # Check if both wishlist_id and product_entry_id are provided
    if not wishlist_id or not product_entry_id:
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. Wishlist ID and Product Entry ID must be filled.'}, status=404)
        add_get_params(response)
        return response

    try:
        # Retrieve the wishlist with the given wishlist_id
        wishlist = session.query(WishList).filter_by(
            id=wishlist_id, user_id=user.id).first()

        # Retrieve the product entry with the given product_entry_id
        product_entry = session.query(ProductEntry).get(product_entry_id)
    except SQLAlchemyError as e:
        session.rollback()
        response = JsonResponse(
            {'answer': False, 'message': 'Error retrieving data from the database.', 'error': str(e)}, status=500)
        add_get_params(response)
        return response

    # Check if the wishlist and product entry exist and if the user is authorized to add products to the wishlist
    if not wishlist or not product_entry:
        response = JsonResponse(
            {'answer': False, 'message': 'Invalid data provided or user is not authorized to add products to the wishlist.'}, status=401)
        add_get_params(response)
        return response

    # Check if the product entry is already in the wishlist
    if session.query(WishListProductEntry).filter_by(wishlist_id=wishlist_id, product_entry_id=product_entry_id).first():
        response = JsonResponse(
            {'answer': False, 'message': 'Product entry is already in the wishlist.'}, status=200)
        add_get_params(response)
        return response

    # Add the product entry to the wishlist and commit the changes to the database
    try:

        # Create a new instance of the WishListProductEntry class and set its attributes
        wishlist_product_entry = WishListProductEntry(
            wishlist_id=wishlist_id, product_entry_id=product_entry_id)

        # Add the new wishlist-product entry association to the session
        session.add(wishlist_product_entry)

        # Commit the changes to the database
        session.commit()

        # Return a JSON response with a success message
        response = JsonResponse(
            {'answer': True, 'message': 'Product entry added to the wishlist.'}, status=200)
        add_get_params(response)
        return response

    # Catch any database errors and rollback the session
    except SQLAlchemyError as e:
        session.rollback()
        # Return a JSON response with an error message and the error details
        response = JsonResponse(
            {'answer': False, 'message': 'Error adding product entry to wishlist.', 'error': str(e)}, status=500)
        add_get_params(response)
        return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_product_entry_in_wishlist(request):
    """
    This function deletes a product entry from a wishlist with the given wishlist_id.
    The function receives the following parameters from the request object:
    - wishlist_id: the ID of the wishlist from which the product entry should be deleted
    - product_entry_id: the ID of the product entry to be deleted from the wishlist
    If the product entry is successfully deleted from the wishlist, the function returns a JSON response with a success message.
    If an error occurs during the product entry deletion process, the function returns a JSON response with an error message and the error details.
    """

    session = request.session
    user = request.person.user[0]

    # Get the parameters from the request object
    wishlist_id = request.data.get("wishlist_id")
    product_entry_id = int(request.data.get("product_entry_id"))

    # Check if both wishlist_id and product_entry_id are provided
    if not wishlist_id or not product_entry_id:
        response = JsonResponse(
            {'answer': False, 'message': 'Missing data error. Wishlist ID and Product Entry ID must be filled.'}, status=404)
        add_get_params(response)
        return response

    try:
        # Retrieve the wishlist with the given wishlist_id and user.id
        wishlist = session.query(WishList).filter_by(
            wishlist_id, user_id=user.id).first()

        # Retrieve the product entry with the given product_entry_id
        product_entry = session.query(ProductEntry).get(product_entry_id)
    except SQLAlchemyError as e:
        session.rollback()
        response = JsonResponse(
            {'answer': False, 'message': 'Error retrieving data from the database.', 'error': str(e)}, status=500)
        add_get_params(response)
        return response

    # Check if the wishlist and product entry exist and if the user is authorized to delete products from the wishlist
    if not wishlist or not product_entry:
        response = JsonResponse(
            {'answer': False, 'message': 'Invalid data provided or user is not authorized to delete products from the wishlist.'}, status=401)
        add_get_params(response)
        return response

    # Check if the product entry is in the wishlist
    wishlist_product_entry = session.query(WishListProductEntry).filter_by(
        wishlist_id=wishlist_id, product_entry_id=product_entry_id).first()
    if not wishlist_product_entry:
        response = JsonResponse(
            {'answer': False, 'message': 'Product entry is not in the wishlist.'}, status=200)
        add_get_params(response)
        return response

    # Delete the product entry from the wishlist and commit the changes to the database
    try:
        # Delete the wishlist-product entry association from the session
        session.delete(wishlist_product_entry)

        # Commit the changes to the database
        session.commit()

        # Return a JSON response with a success message
        response = JsonResponse(
            {'answer': True, 'message': 'Product entry deleted from the wishlist.'}, status=200)
        add_get_params(response)
        return response

    # Catch any database errors and rollback the session
    except SQLAlchemyError as e:
        session.rollback()
        # Return a JSON response with an error message and the error details
        response = JsonResponse(
            {'answer': False, 'message': 'Error deleting product entry from wishlist.', 'error': str(e)}, status=500)
        add_get_params(response)
        return response


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_product_entry_in_wishlist_with_id(request, wishlist_product_entry_id):
    session = request.session
    user = request.person.user[0]
    try:
        # Retrieve the wishlist-product entry with the given ID
        wishlist_product_entry = session.query(
            WishListProductEntry).get(wishlist_product_entry_id)

        # Check if the wishlist-product entry and product entry exist and if the user is authorized to delete products from the wishlist
        if (
            not wishlist_product_entry
            or wishlist_product_entry.wishlist.user_id != user.id
        ):
            response = JsonResponse(
                {'answer': False, 'message': 'Invalid data provided or user is not authorized to delete products from the wishlist.'}, status=401)
            add_get_params(response)
            return response

        # Delete the wishlist-product entry from the session and commit the changes to the database
        session.delete(wishlist_product_entry)
        session.commit()

        # Return a JSON response with a success message
        response = JsonResponse({'Success': 'The wishlist product entry has been successfully deleted.',
                                "wishlist_product_entry_id": wishlist_product_entry_id}, status=200)
        add_get_params(response)
        return response

    except SQLAlchemyError as e:
        session.rollback()
        response = JsonResponse(
            {'Success': 'False', 'message': 'An error occurred while deleting the wishlist product entry.', 'error_details': str(e)}, status=500)
        add_get_params(response)
        return response
