import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sqlalchemy.exc import SQLAlchemyError
from DjApp.decorators import login_required, require_http_methods
from ..models import ProductEntry, WishList, WishListProductEntry



def create_wishlist_func(title,user, session):
    """
    This function handles the creation of a new wishlist for a user.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user for which the wishlist should be created
    - title: the title of the wishlist to be created
    If the wishlist creation is successful, the function returns a JSON response with a success message and the new wishlist's information.
    If an error occurs during the wishlist creation process, the function returns a JSON response with an error message and the error details.
    """


    if not (user or title):
        return JsonResponse(
            {
                'answer': 'successful',
                'message': 'Missing data error. User ID and Title must be filled.',
            },
            status=404,
        )
    # check user is exist
    if (
        session.query(WishList)
        .filter_by(user_id=user.id, title=title)
        .first()
    ):
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'The user already has a wishlist with this title.',
            },
            status=404,
        )
    # Add the new wishlist to the database and commit the changes
    new_wishlist = WishList(
        user_id=user.id,
        title=title
    )

    session.add(new_wishlist)
    session.commit()

    return JsonResponse(
        {   'answer':'successful',
            'message': 'The new wishlist has been successfully created.',
            "wishlist": new_wishlist.to_json(),
        },
        status=200,
    )





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
    user = request.person.user
    session = request.session

    return create_wishlist_func(title, user, session)





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
    user = request.person.user
    session = request.session

    if not (wishlist_id or title):
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Missing data error. Wishlist ID and Title must be filled.',
            },
            status=404,
        )
    if not user:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'User with the given ID does not exist.',
            },
            status=404,
        )
    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).filter_by(
        id=wishlist_id, user_id=user.id).first()
    if not wishlist:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'The user does not have a wishlist with this ID.',
            },
            status=404,
        )
    # Update the wishlist title with the new title parameter
    wishlist.title = title
    session.commit()

    return JsonResponse(
        {   'answer':'successful',
            'message': 'The wishlist title has been successfully updated.',
            "wishlist_id": wishlist.id,
            'user_id': user.id,
            'title': wishlist.title,
        },
        status=200,
    )


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
    user = request.person.user
    session = request.session

    if not wishlist_id:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Missing data error. Wishlist ID must be filled.',
            },
            status=404,
        )
    if not user:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'User with the given ID does not exist.',
            },
            status=404,
        )
    # Check if the wishlist exists for the given user
    wishlist = session.query(WishList).filter_by(
        id=wishlist_id, user_id=user.id).first()
    if not wishlist:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'The user does not have a wishlist with this ID.',
            },
            status=404,
        )
    # Delete the wishlist
    session.delete(wishlist)
    session.commit()

    return JsonResponse(
        {
            'answer': 'successful',
            'message': 'The wishlist has been successfully deleted.'}, status=200
        )


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
    user = request.person.user

    # Get the parameters from the request object
    wishlist_id = request.data.get("wishlist_id")
    product_entry_id = int(request.data.get("product_entry_id"))

    # Check if both wishlist_id and product_entry_id are provided
    if not product_entry_id:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Missing data error. Wishlist ID and Product Entry ID must be filled.',
            },
            status=404,
        )

    try:
        # Retrieve the wishlist with the given wishlist_id
        if not wishlist_id:
            wishlist = session.query(WishList).filter_by(user_id=user.id).first()
        else:
            wishlist = session.query(WishList).filter_by(id=wishlist_id, user_id=user.id).first()

        # Retrieve the product entry with the given product_entry_id
        product_entry = session.query(ProductEntry).get(product_entry_id)

        # Check if the wishlist and product entry exist and if the user is authorized to add products to the wishlist
        if not wishlist:
            create_wishlist_func("Default", user, session)
            wishlist = session.query(WishList).filter_by(user_id=user.id).first()

        if not wishlist or not product_entry:
            return JsonResponse(
                {
                    'answer': 'unsuccessful',
                    'message': 'Invalid data provided or user is not authorized to add products to the wishlist.',
                },
                status=401,
            )

        # Check if the product entry is already in the wishlist
        if session.query(WishListProductEntry).filter_by(wishlist_id=wishlist.id, product_entry_id=product_entry_id).first():
            return JsonResponse(
                {
                    'answer': 'unsuccessful',
                    'message': 'Product entry is already in the wishlist.',
                    'wishlist': wishlist.to_json_light(),
                },
                status=200,
            )

        # Add the product entry to the wishlist and commit the changes to the database
        wishlist_product_entry = WishListProductEntry(wishlist_id=wishlist.id, product_entry_id=product_entry_id)
        session.add(wishlist_product_entry)
        session.commit()

        return JsonResponse(
            {
                'answer': 'successful',
                'message': 'Product entry added to the wishlist.',
                'wishlist': wishlist.to_json_light(),
            },
            status=200,
        )

    except SQLAlchemyError as e:
        session.rollback()
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Error adding product entry to wishlist.',
                'wishlist': wishlist.to_json_light(),
                'error': str(e),
            },
            status=500,
        )

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
    user = request.person.user

    # Get the parameters from the request object
    wishlist_id = request.data.get("wishlist_id")
    product_entry_id = int(request.data.get("product_entry_id"))

    # Check if both wishlist_id and product_entry_id are provided
    if not wishlist_id or not product_entry_id:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Missing data error. Wishlist ID and Product Entry ID must be filled.',
            },
            status=404,
        )
    try:
        # Retrieve the wishlist with the given wishlist_id and user.id
        wishlist = session.query(WishList).filter_by(id=wishlist_id, user_id=user.id).first()

        # Retrieve the product entry with the given product_entry_id
        product_entry = session.query(ProductEntry).get(product_entry_id)
    except SQLAlchemyError as e:
        session.rollback()
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Error retrieving data from the database.',
                'error': str(e),
            },
            status=500,
        )
    # Check if the wishlist and product entry exist and if the user is authorized to delete products from the wishlist
    if not wishlist or not product_entry:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Invalid data provided or user is not authorized to delete products from the wishlist.',
            },
            status=401,
        )
    # Check if the product entry is in the wishlist
    wishlist_product_entry = session.query(WishListProductEntry).filter_by(
        wishlist_id=wishlist_id, product_entry_id=product_entry_id).first()
    if not wishlist_product_entry:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Product entry is not in the wishlist.',
            },
            status=200,
        )
    # Delete the product entry from the wishlist and commit the changes to the database
    try:
        # Delete the wishlist-product entry association from the session
        session.delete(wishlist_product_entry)

        # Commit the changes to the database
        session.commit()

        return JsonResponse(
            {
                'answer': 'successful',
                'message': 'Product entry deleted from the wishlist.',
            },
            status=200,
        )
    except SQLAlchemyError as e:
        session.rollback()
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'Error deleting product entry from wishlist.',
                'error': str(e),
            },
            status=500,
        )



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_product_entry_in_wishlist_with_id(request, wishlist_product_entry_id):
    session = request.session
    user = request.person.user
    try:
        # Retrieve the wishlist-product entry with the given ID
        wishlist_product_entry = session.query(
            WishListProductEntry).get(wishlist_product_entry_id)

        # Check if the wishlist-product entry and product entry exist and if the user is authorized to delete products from the wishlist
        if (
            not wishlist_product_entry
            or wishlist_product_entry.wishlist.user_id != user.id
        ):
            return JsonResponse(
                {
                    'answer': 'unsuccessful',
                    'message': 'Invalid data provided or user is not authorized to delete products from the wishlist.',
                },
                status=401,
            )
        # Delete the wishlist-product entry from the session and commit the changes to the database
        session.delete(wishlist_product_entry)
        session.commit()

        return JsonResponse(
            {
                'answer': 'successful',
                'message': 'The wishlist product entry has been successfully deleted.',
                "wishlist_product_entry_id": wishlist_product_entry_id,
            },
            status=200,
        )
    except SQLAlchemyError as e:
        session.rollback()
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'An error occurred while deleting the wishlist product entry.',
                'error_details': str(e),
            },
            status=500,
        )
