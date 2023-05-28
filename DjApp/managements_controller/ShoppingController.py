import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjApp.models import CartItem, Discount, ProductEntry, ProductDiscount, ShoppingSession
from ..helpers import GetErrorDetails
from ..decorators import login_required, require_http_methods


@csrf_exempt
def create_shopping_session(request):
    """
    This function handles the creation of a new shopping session by adding a new entry in the 'shopping_session' table.
    The function receives the following parameters from the request object:
    - user_id: the id of the user creating the session
    - total: the total cost of the items in the session

    If the session creation is successful, the function returns a JSON response with a success message and the new session's information.
    If an error occurs during the session creation process, the function returns a JSON response with an error message and the error details.
    """
    session = request.session

    # Get the parameters from the request object
    user_id = request.person.user[0].id
    new_session = ShoppingSession(user_id=user_id,
                                  total=0)
    # Add the new session to the database and commit the changes
    request.shopping_session = new_session
    session.add(new_session)

    return new_session


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_to_basket(request):
    """
    API endpoint to add a product_entry to a user's shopping session.
    The request should contain the following parameters:
    - session_id: the ID of the shopping session to add the product_entry to
    - product_entry_id: the ID of the product_entry to add
    - quantity: the quantity of the product_entry to add
    """
    # Get the user object associated with the request
    user = request.person.user[0]
    session = request.session
    data = request.data

    # Get the parameters from the request
    product_entry_id = data.get('product_entry_id')
    quantity = int(data.get('quantity')) if data.get('quantity') else None
    # Get the shopping session associated with the specified session ID and user ID
    shopping_session = session.query(
            ShoppingSession).filter_by(user_id=user.id).first() or create_shopping_session(request)

    # Get the product_entry associated with the specified product_entry ID
    product_entry = session.query(ProductEntry).get(product_entry_id)
    if not product_entry:
        return JsonResponse(
            {'answer': "Invalid product_entry id."}, status=400
        )
    cart_item = session.query(CartItem).filter_by(
        session_id=shopping_session.id, product_entry_id=product_entry_id).first()
    if not cart_item:
        # Add the product_entry to the shopping session with the specified quantity
        cart_item = (
            CartItem(
                session_id=shopping_session.id,
                product_entry_id=product_entry_id,
                quantity=quantity,
            )
            if quantity is not None
            else CartItem(
                session_id=shopping_session.id,
                product_entry_id=product_entry_id,
                quantity=1,
            )
        )
        session.add(cart_item)
        session.commit()
    elif quantity is not None:
        cart_item.quantity = quantity
    else:
        cart_item.quantity = cart_item.quantity + 1

    cart_item_total = cart_item.total()

    discount = session.query(Discount).join(ProductDiscount).filter(
        ProductDiscount.product_entry_id == product_entry.id).first()
    discount_data = {}
    if discount and discount.active:

        discount_price = float(cart_item_total) * \
            float(discount.discount_percent)/100

        discount_data['name'] = discount.name
        discount_data['percent'] = discount.discount_percent/100
        discount_data['description'] = discount.description
        discount_data['discount_price'] = discount_price

    return JsonResponse(
        {
            "answer": "The add_or_change cart item precess successfully finished.",
            "product_name": product_entry.product.name,
            "product_entry_price": product_entry.price,
            "product_id": product_entry.product.id,
            "product_entry_id": product_entry.id,
            "cart_item_id": cart_item.id,
            "cart_item_quantity": cart_item.quantity,
            "cart_item_total": cart_item_total,
            "discount_data": discount_data or "Not any discount",
            "shopping_session_id": shopping_session.id,
            "user_id": user.id,
        },
        status=200,
    )
@csrf_exempt
@require_http_methods(["POST"])
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_cart_item_status(request, cart_item_id):
    """
    API endpoint to update a cart item in a user's shopping session.
    The request should contain the following parameters:
    - cart_item_id: the ID of the cart item to update
    - quantity: the new quantity of the cart item
    """
    # Get the user object associated with the request
    user = request.person.user[0]
    session = request.session

    # Get the cart item to update
    cart_item = session.query(CartItem).get(cart_item_id)
    if not cart_item:
        return JsonResponse(
            {'answer': "The cart item could not be found."}, status=400
        )
    # Get the shopping session associated with the specified user ID
    shopping_session = user.shopping_session[0]
    if cart_item.session_id != shopping_session.id:
        return JsonResponse(
            {'answer': "The cart item is not this user."}, status=400
        )
    cart_item.status = 'inOrder' if cart_item.status == 'inCart' else 'inCart'

    # Commit changes to the database
    session.commit()

    return JsonResponse(
        {
            "answer": "The cart item has been updated successfully.",
            "cart_item": cart_item.to_json(),
        },
        status=200,
    )
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_cart_item(request, cart_item_id):
    """
    API endpoint to delete a cart item from a user's shopping session.
    The request should contain the following parameters:
    - cart_item_id: the ID of the cart item to delete
    """
    # Get the user object associated with the request
    user = request.person.user[0]
    session = request.session

    # Get the cart item to delete
    cart_item = session.query(CartItem).get(cart_item_id)
    if not cart_item:
        return JsonResponse(
            {'answer': "The cart item could not be found."}, status=400
        )
    # Get the shopping session associated with the specified user ID

    shopping_session = user.shopping_session[0]
    if cart_item.session_id != shopping_session.id:
        return JsonResponse(
            {'answer': "The cart item is not this user."}, status=400
        )
    # Delete the cart item
    session.delete(cart_item)

    return JsonResponse(
        {
            "answer": "The cart item has been deleted successfully.",
            "cart_item_id": cart_item.id,
            "shopping_session_id": shopping_session.id,
            "shopping_session_total": shopping_session.total(),
            "user_id": user.id,
        },
        status=200,
    )
