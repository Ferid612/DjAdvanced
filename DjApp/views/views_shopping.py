import datetime
from django.http import JsonResponse
from sqlalchemy import func
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings import engine
from DjApp.models import CartItem,  Product, ProductEntry,  ShoppingSession, UserPayment
from ..helpers import  add_get_params
from ..decorators import login_required, require_http_methods
from sqlalchemy.orm import joinedload




# Helper functions for calculating discounts and cargo fees
@csrf_exempt
def calculate_discounts(cart_item):
    discounts = cart_item.product_entry.discount
    active_discounts = [d for d in discounts if d.discount.active]
    discount_price = sum(cart_item.total() * float(d.discount.discount_percent) for d in active_discounts)
    return discount_price




@csrf_exempt
def calculate_discount_data(cart_item):
    discounts = cart_item.product_entry.discount
    active_discounts = [d for d in discounts if d.discount.active]
    if active_discounts:
        discount_percent = float(active_discounts[0].discount.discount_percent)
        cart_item_total = cart_item.total()
        discount_price = cart_item_total * discount_percent
        discount_data = {
            'name': active_discounts[0].discount.name,
            'percent': discount_percent,
            'description': active_discounts[0].discount.description,
            'discount_price': discount_price
        }
        return discount_data
    else:
        return "Not any discount"


            
@csrf_exempt
def calculate_cargo_fee(cart_item):
    product_entry = cart_item.product_entry
    if product_entry.cargo_active:
        if product_entry.product.supplier.cargo_percent:
            cargo_percent = float(product_entry.product.supplier.cargo_percent)
        else:
            cargo_percent=0
        return cart_item.total() * cargo_percent
    return 0



@csrf_exempt
def calculate_cargo_data(cart_item):
    product_entry = cart_item.product_entry
    cargo_data = {}
    if product_entry.cargo_active:
        cargo_percent = float(product_entry.product.supplier.cargo_percent)
        item_cargo_fee = cart_item.total() * cargo_percent 
        cargo_data['supplier_cargo_percent'] = cargo_percent
        cargo_data['item_cargo_fee'] = item_cargo_fee
    else:
        cargo_data = "Not any cargo fee"
    return cargo_data





@csrf_exempt
def calculate_supplier_prices_and_cargo_discounts(cart_items,amount_to_be_paid):
    """
    Calculates the total price of each supplier's products and applies cargo discounts if applicable.
    Returns a tuple of (supplier_prices, supplier_cargo_discounts, amount_to_be_paid)
    """
    supplier_prices = {}
    for cart_item in cart_items:
        product_entry = cart_item.product_entry
        if product_entry.cargo_active:
            supplier = product_entry.product.supplier
            price = product_entry.price * cart_item.quantity
            if supplier not in supplier_prices:
                supplier_prices[supplier] = price
            else:
                supplier_prices[supplier] += price


    supplier_cargo_discounts = {}
    for supplier, price in supplier_prices.items():
        if not supplier.cargo_min_limit:
            supplier.cargo_min_limit = 1.0
            supplier.cargo_percent = 0.0
        if (price > supplier.cargo_min_limit):
            cargo_discount = float(supplier.cargo_percent) * price
            supplier_cargo_discounts[supplier.name] = cargo_discount
            amount_to_be_paid -= cargo_discount

    return supplier_prices, supplier_cargo_discounts, amount_to_be_paid




def get_product_entry_price_after_discount(session, product_entry_id):
    """
    Returns the price of a product entry after applying any active discounts.
    """
    product_entry = session.query(ProductEntry).get(product_entry_id)

    discounts = product_entry.discount
    active_discounts = [d.discount for d in discounts if d.discount.active]
    if active_discounts:
        discount_percent = float(active_discounts[0].discount_percent)
        discounted_price = product_entry.price * (1 - discount_percent)
        return discounted_price
    else:
        return product_entry.price


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
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
        return JsonResponse({'answer': "The session data of the user could not be found."}, status=400)


    # Eager load related data
    cart_items = session.query(CartItem).options(
        joinedload(CartItem.product_entry).joinedload(ProductEntry.discount)
    ).filter_by(session_id=shopping_session.id).all()

    shopping_session_total = shopping_session.total()

    # Calculate discounts and cargo fees
    whole_discounts = sum(calculate_discounts(cart_item) for cart_item in cart_items)
    whole_cargo_fee = sum(calculate_cargo_fee(cart_item) for cart_item in cart_items)

    # Calculate total amount to be paid
    amount_to_be_paid = shopping_session_total - whole_discounts + whole_cargo_fee

    supplier_prices, supplier_cargo_discounts, amount_to_be_paid = calculate_supplier_prices_and_cargo_discounts(cart_items, amount_to_be_paid)


    # Process cart items
    # Group cart items by supplier name
    cart_item_data = {}
    for cart_item in cart_items:
        supplier_name = cart_item.product_entry.product.supplier.name
        if supplier_name not in cart_item_data:
            cart_item_data[supplier_name] = []
        cart_item_data[supplier_name].append({
            'id': cart_item.id,
            'quantity': cart_item.quantity,
            'cart_item_total': cart_item.total(),
            'discount_data': calculate_discount_data(cart_item),
            'cargo_data': calculate_cargo_data(cart_item),
            'product': {
                'id': cart_item.product_entry.id,
                'name': cart_item.product_entry.product.name,
                'description': cart_item.product_entry.product.description,
                'price': cart_item.product_entry.price,
                'category_name': cart_item.product_entry.product.category.name
            }
        })
        
        

    response_data = {
        'username': person.username,
        'total': shopping_session_total,
        'whole_discounts': whole_discounts,
        'whole_cargo_fee': whole_cargo_fee,
        'supplier_cargo_discounts': supplier_cargo_discounts,
        
        'amount_to_be_paid': amount_to_be_paid,
        'cart_items': cart_item_data
    }
    response = JsonResponse(response_data)
    add_get_params(response)
    return response





