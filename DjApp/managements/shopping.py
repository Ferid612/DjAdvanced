import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import CardItem, Product, ShoppingSession, UserPayment
from ..helpers import GetErrorDetails, add_get_params, session_scope
from ..decorators import login_required, require_http_methods



@csrf_exempt
@require_http_methods(["POST"])
@login_required
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
    user_id = request.user.id
    new_session = ShoppingSession(user_id=user_id,
                                total=0,
                                created_at=datetime.datetime.utcnow(),
                                modified_at=datetime.datetime.utcnow()
                                )
    # Add the new session to the database and commit the changes
    request.shopping_session = new_session
    session.add(new_session)

    # Return a JSON response with a success message and the new session's information
    response = JsonResponse({"Success":"The new shopping session has been successfully created.","session_id": new_session.id,"total": 0, "user_id": user_id, "created_at": new_session.created_at, "modified_at": new_session.modified_at}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_shopping_session(request):
    """
    This function handles the updating of an existing shopping session by modifying the entry in the 'shopping_session' table with the given session_id.
    The function receives the following parameters from the request object:
    - session_id: the id of the session to be updated
    - total: the total cost of the items in the session
    If the session update is successful, the function returns a JSON response with a success message and the updated session's information.
    If an error occurs during the session update process, the function returns a JSON response with an error message and the error details.
    """
    try:


        # Get the parameters from the request object
        user_id = request.user.id
        session = request.session
        
        
        # Get the session to be updated
        shopping_session = session.query(ShoppingSession).filter_by(user_id=user_id).first()
        
        if shopping_session is None:
            create_shopping_session(request)
            shopping_session = request.shopping_session
            
        total_of_all_items = session.query(func.sum(Product.price)).join(CardItem).filter(CardItem.session_id==shopping_session.id).all()
        
        print(total_of_all_items)
        
        # Update the session object with the given parameters
        shopping_session.total = 0
        shopping_session.modified_at = datetime.datetime.utcnow()

        # Return a JSON response with a success message and the updated session's information
        response = JsonResponse({"Success":"The shopping session has been successfully updated.","session_id": shopping_session.id,"total": 0, "user_id": shopping_session.user_id, "created_at": shopping_session.created_at, "modified_at": shopping_session.modified_at}, status=200)
        add_get_params(response)
        return response
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when updating the shopping session.", e, 500)
        add_get_params(response)
        return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_card_item(request):
    """
    This function handles the creation of a new card item by adding a new entry in the 'card_item' table.
    The function receives the following parameters from the request object:
    - session_id: the id of the shopping session the item belongs to
    - product_id: the id of the product added to the card
    If the card item creation is successful, the function returns a JSON response with a success message and the new item's information.
    If an error occurs during the card item creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    
    data = request.data
    session = request.session

    user_id = data.get('user_id')
    product_id = data.get('product_id')

    # Start a new database session

    shopping_session = session.query(ShoppingSession).filter_by(user_id=user_id).first()


    if not shopping_session:
        create_shopping_session(request)
        shopping_session = request.shopping_session

    # response = JsonResponse({"answer":"falses","message": "something went wrong", "message_2": "session is already have for this user"}, status=404)
    # add_get_params(response)
    # return response
    
    card_item = session.query(CardItem).filter_by(session_id=shopping_session.id).first()

    if card_item:
    # Getting the value of _quantity
        quantity = card_item.quantity
        quantity+=1
        # Setting the value of _quantity
        card_item.quantity = quantity

    else:                   
        # Create a new card item object with the given parameters
        new_item = CardItem(session_id=shopping_session.id,
                            product_id=product_id,
                            quantity = 1,
                            created_at=datetime.datetime.utcnow(),
                            modified_at=datetime.datetime.utcnow()
                            )
        # Add the new item to the database and commit the changes
        session.add(new_item)
        
            

    # Return a JSON response with a success message and the new item's information
    response = JsonResponse({"Success":"The new card item has been successfully created.","item_id": new_item.id, "session_id": shopping_session.id, "product_id": product_id, "created_at": new_item.created_at, "modified_at": new_item.modified_at}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_card_item(request):
    """
    This function handles the update of an existing card item by updating an entry in the 'card_item' table.
    The function receives the following parameters from the request object:
    - session_id: the id of the shopping session the item belongs to
    - product_id: the id of the product being added to the cart
    If the item update is successful, the function returns a JSON response with a success message and the updated item's information.
    If an error occurs during the item update process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    data = request.data
    session = request.session

    item_id = data.get('item_id')
    session_id = data.get('session_id')
    product_id = data.get('product_id')

    # Retrieve the existing card item from the database
    card_item = session.query(CardItem).filter_by(id=item_id).first()

    # Update the card item with the given parameters
    card_item.session_id = session_id
    card_item.product_id = product_id
    card_item.modified_at = datetime.datetime.utcnow()

    # Return a JSON response with a success message and the updated item's information
    response = JsonResponse({"Success":"The card item has been successfully updated.","item_id": card_item.id,"session_id": session_id, "product_id": product_id, "created_at": card_item.created_at, "modified_at": card_item.modified_at}, status=200)
    add_get_params(response)
    return response

