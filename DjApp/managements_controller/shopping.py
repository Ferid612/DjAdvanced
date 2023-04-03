import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import CartItem, Discount, Product, ProductDiscount, ShoppingSession, UserPayment
from ..helpers import GetErrorDetails, add_get_params, session_scope
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
            
        total_of_all_items = session.query(func.sum(Product.price)).join(CartItem).filter(CartItem.session_id==shopping_session.id).all()
        
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
def add_or_change_product_in_shopping_session(request):
    """
    API endpoint to add a product to a user's shopping session.
    The request should contain the following parameters:
    - session_id: the ID of the shopping session to add the product to
    - product_id: the ID of the product to add
    - quantity: the quantity of the product to add
    """
    try:
        # Get the user object associated with the request
        user = request.person.user[0]
        session = request.session
        data = request.data
        
        # Get the parameters from the request
        product_id = data.get('product_id')
        quantity = int(data.get('quantity'))
    
    
        # Get the shopping session associated with the specified session ID and user ID
        shopping_session = session.query(ShoppingSession).filter_by(user_id=user.id).first()
        if not shopping_session:
            shopping_session = create_shopping_session(request)

                        
        # Get the product associated with the specified product ID
        product = session.query(Product).get(product_id)
        if not product:
            # If phone number already exists, return an error response
            response = JsonResponse({'answer': "Invalid product id."}, status=400)

            add_get_params(response)
            return response


        cart_item = session.query(CartItem).filter_by(session_id=shopping_session.id, product_id=product_id).first()
        if not cart_item:
            # Add the product to the shopping session with the specified quantity
            cart_item = CartItem(session_id=shopping_session.id, product_id=product_id, quantity=quantity)
            session.add(cart_item)
            session.commit()
        else:
            cart_item.quantity = quantity

        
        cart_item_total = cart_item.total()
        
        discount = session.query(Discount).join(ProductDiscount).filter(ProductDiscount.product_id == product.id).first()
        discount_data={}
        if discount and discount.active :
            
            discount_price =  cart_item_total * discount.discount_percent             
            
            discount_data['name'] = discount.name
            discount_data['percent'] = discount.discount_percent
            discount_data['description'] = discount.description
            discount_data['discount_price'] = discount_price

        
        
        
        # Return a success response
        response = JsonResponse(
            {"answer": "The add_or_change cart item precess successfully finished.",
             "product_name":product.name,
             "product_price":product.price,
             "product_id":product.id,
             "cart_item_id":cart_item.id,
             "cart_item_quantity":cart_item.quantity,
             "cart_item_total":cart_item_total,
             "discount_data": discount_data or "Not any discount",
            "shopping_session_id":shopping_session.id,
            "user_id":user.id
             },
            status=200
        )
        add_get_params(response)
        
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details if an exception occurs
        response = GetErrorDetails("An error occurred while adding the product to the shopping session.", e, 500)
        add_get_params(response)
        return response


    
    
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_cart_item(request):
    """
    API endpoint to delete a cart item from a user's shopping session.
    The request should contain the following parameters:
    - cart_item_id: the ID of the cart item to delete
    """
    try:
        # Get the user object associated with the request
        user = request.person.user[0]
        session = request.session
        data = request.data
        
        # Get the parameters from the request
        cart_item_id = data.get('cart_item_id')
    
        # Get the shopping session associated with the specified user ID
        shopping_session = session.query(ShoppingSession).filter_by(user_id=user.id).first()
        if not shopping_session:
            response = JsonResponse({'answer': "The session data of the user could not be found."}, status=400)
            add_get_params(response)
        
            return response
        
        # Get the cart item to delete
        cart_item = session.query(CartItem).get(cart_item_id)
        if not cart_item:
            response = JsonResponse({'answer': "The cart item could not be found."}, status=400)
            add_get_params(response)
            return response
        
        # Delete the cart item
        session.delete(cart_item)
        
        # Return a success response
        response = JsonResponse(
            {"answer": "The cart item has been deleted successfully.",
             "cart_item_id": cart_item.id,
             "shopping_session_id":shopping_session.id,
             "shopping_session_total":shopping_session.total(),
             "user_id":user.id
            },
            status=200
        )
        
            
        add_get_params(response)
        return response
        
    except Exception as e:
        # Return a JSON response with an error message and the error details if an exception occurs
        response = GetErrorDetails("An error occurred while deleting the cart item from the shopping session.", e, 500)
        add_get_params(response)
        return response