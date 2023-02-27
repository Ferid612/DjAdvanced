import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import cartItem, Discount, Product, ProductDiscount, ShoppingSession, UserPayment
from ..helpers import GetErrorDetails, add_get_params, session_scope
from ..decorators import login_required, require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def get_user_shopping_session_data(request):
    """
    Retrieves all the cart items for the authenticated user and returns them along with the corresponding product data.
    """
    person = request.person
    user = person.user[0]
    session = request.session

    shopping_session = session.query(ShoppingSession).filter_by(user_id=user.id).first()
    if not shopping_session:        
        response = JsonResponse({'answer': "The session data of the user could not be found."}, status=400)
        return response

        
    # Get all cart items for the user
    cart_items = session.query(cartItem).filter_by(session_id=shopping_session.id).all()

    shopping_session_total = shopping_session.total()
    amount_to_be_paid = shopping_session_total
    whole_discounts = 0
    


    # Get product data for each cart item
    cart_item_data = []
    for cart_item in cart_items:
        product = session.query(Product).get(cart_item.product_id)
        if product:
            
            discount = session.query(Discount).join(ProductDiscount).filter(ProductDiscount.product_id == product.id).first()
            discount_data={}
            cart_item_total = cart_item.total()
            if discount and discount.active :
                discount_price =  cart_item_total * float(discount.discount_percent)             
                discount_data['name'] = discount.name
                discount_data['percent'] = discount.discount_percent
                discount_data['description'] = discount.description
                discount_data['discount_price'] = discount_price
                amount_to_be_paid -= discount_price
                whole_discounts += discount_price
                
    
            cart_item_data.append({
                'id': cart_item.id,
                'quantity': cart_item.quantity,
                'cart_item_total': cart_item_total,
                "discount_data": discount_data or "Not any discount",
        
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'supplier_name': product.supplier.name,
                    'subcategory_name': product.subcategory.name
                    
                    
                }
            })


    response =  JsonResponse({
        'username':person.username,
        'total':shopping_session_total,
        'whole_discounts':whole_discounts,
        'amount_to_be_paid':amount_to_be_paid,
        'cart_items': cart_item_data})
    add_get_params(response)
    
    return response