from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjAdvanced.settings.base import EMAIL_HOST_USER
from DjApp.controllers.MailController import send_email
from DjApp.models import CashPayment, CreditCard, CreditCardPayment, DiscountCoupon, DiscountCouponUser, Order, OrderItem, Payment
from ..helpers import create_pdf, json_object_to_html
from ..decorators import login_required, require_http_methods



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def CompleteOrder(request):
    """
    API endpoint to complete an order.
    The request should contain the following parameters:
    - session_id: the ID of the shopping session to add the product_entry to
    - payment_method: the payment method to use for the order (cash or credit_card)
    - If payment method is credit_card, the request should also contain the following parameters:
        - card_number: the credit card number
        - cvv: the credit card CVV code
        - expiration_date: the credit card expiration date in the format YYYY-MM-DD
        - save_credit_card: a boolean indicating whether to save the credit card information for future orders
    """

    session = request.session
    try:
        person = request.person
        user = person.user
        shopping_session = user.shopping_session[0]
        cart_items_in_order = get_cart_items_in_order(shopping_session)
        new_order = create_order(session, user, cart_items_in_order)
        payment = create_payment(new_order, request)
        handle_credit_card_payment(payment, request)
        handle_cash_payment(session, payment)

        payment.status = 'completed'

        delete_items_from_cart(session, cart_items_in_order)
        session.commit()
        
        order_details = new_order.to_json()
        
        person_firstname = person.first_name
        person_lastname = person.last_name
        report_type = "Order Details"

        
        now_date = datetime.now().strftime("%Y-%m-%d__%H:%M:%S")
        file_name = f"{person_firstname}_{person_lastname}_order_details_{now_date}.pdf"

        # Generate the PDF
        pdf = create_pdf(file_name, person_firstname, person_lastname, report_type, order_details)
        
        # Create an HTTP response with the PDF file    
        response = HttpResponse(bytes(pdf.output()), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
    
    except Exception as e:
        print("here is working error")
        try:
            payment.status = 'failed'
            new_order.status = 'cancelled'
        except Exception as exc:
            print(exc)

        session.rollback()
        raise e



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def change_order_status(request):
    """
    Updates the status of an order.

    Args:
        request: HttpRequest object representing the current request.

    Returns:
        JsonResponse: JSON response indicating the success or failure of the operation.
    """
    
    session = request.session
    order_id = request.data.get('order_id')
    new_status = request.data.get('new_status')
    
    order = session.query(Order).get(order_id)

    if order is None:
      return JsonResponse({'error': 'Order not found.'}, status=400)
  
    allowed_statuses = ('preparing', 'placed', 'shipped', 'delivered', 'cancelled')

    if new_status not in allowed_statuses:
       return JsonResponse({'error': 'Invalid status.'}, status=400)


    order.status = new_status
    session.commit()

    return JsonResponse({
        
        'answer':'successfull',
        'message': 'Order status updated successfully.',
        'order': order.to_json()
    
    }, status=200)







@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_order_cancellation_request(request):
    """
    Updates the status of an order.

    Args:
        request: HttpRequest object representing the current request.

    Returns:
        JsonResponse: JSON response indicating the success or failure of the operation.
    """
    session = request.session
    order_id = request.data.get('order_id')
    person = request.person

    order = session.query(Order).get(order_id)
    if order is None:
        return JsonResponse({
            'answer':'unsuccessful',
            'message': 'Order not found.'}, status=400)

    if order.status in ['cancelled', 'delivered']:
        
        return JsonResponse({
            'answer':'unsuccessful',
            'message': f"The order status is {order.status}. The order can't be cancelled."}, status=501)
        
        

    person_data_html = json_object_to_html(person.to_json()) 
    
    # order_details = order.to_json()
    # order_details_str = "<br>".join(f"{key}: {value}" for key, value in order_details.items())

    order_details_html = json_object_to_html(order.to_json())


    body_message = f"User with {person.username} wants to cancel his or her order. <br><br> User data: <br>{person_data_html}<br><br> Order details: <br>{order_details_html}"


    send_email(EMAIL_HOST_USER, f"User with {person.username} wants to cancel his or her order.", body_message)

    return JsonResponse({
        'answer': 'successful',
        'message': 'Order status update request sent successfully.',
        'order': order.to_json()
    }, status=200)


def get_cart_items_in_order(shopping_session):
    # sourcery skip: raise-specific-error
    cart_items_in_order = [
        cart_item for cart_item in shopping_session.cart_items if cart_item.status == 'inOrder']
    if not list(cart_items_in_order):
        print("No cart items")
        raise Exception(
            "No items found to be purchased. Please check your basket.")
    return cart_items_in_order


def create_order(session, user, cart_items_in_order):
    total_price = 0
    new_order = Order(user_id=user.id, total_price=0, status='preparing')
    session.add(new_order)
    session.commit()
    for cart_item in cart_items_in_order:
        current_price = cart_item.product_entry.discount_data.get(
            'discounted_price')
        total_price = total_price + current_price * cart_item.quantity
        new_order_item = OrderItem(
            order_id=new_order.id,
            product_entry_id=cart_item.product_entry.id,
            quantity=cart_item.quantity,
            price=current_price
        )
        session.add(new_order_item)

    active_coupon = session.query(DiscountCoupon).join(DiscountCouponUser).filter(
        DiscountCouponUser.user_id == user.id,
        DiscountCouponUser.is_active == True,
        DiscountCoupon.valid_from <= datetime.now(),
        DiscountCoupon.valid_to >= datetime.now()
    ).first()

    if active_coupon is not None:
        coupon_discount = active_coupon.discount
        new_order.discount_coupon_id = active_coupon.id
        total_price = total_price - coupon_discount

        # Unassign the coupon from the user
        user.discount_coupons.remove(active_coupon)
        session.commit()

    total_price = max(total_price, 0)
    new_order.total_price = total_price
    session.commit()
    return new_order


def delete_items_from_cart(session, cart_items_in_order):
    for cart_item in cart_items_in_order:
        session.delete(cart_item)
    session.commit()


def create_payment(new_order, request):
    session = request.session

    payment = Payment(
        order_id=new_order.id,
        amount=new_order.total_price,
        status='pending',
        payment_method=request.data.get('payment_method')
    )
    session.add(payment)
    session.commit()
    return payment


def handle_credit_card_payment(payment, request):
    if payment.payment_method == 'credit_card':
        credit_card_payment = CreditCardPayment(
            payment_id=payment.id,
            card_number=request.data.get('card_number'),
            cvv=request.data.get('cvv'),
            expiration_date=request.data.get('expiration_date')
        )
        
        session = request.session
        session.add(credit_card_payment)

        if request.data.get('save_credit_card', False):
            handle_saved_credit_card(request)
        session.commit()


def handle_saved_credit_card(request):
    user = request.person.user
    saved_card = CreditCard(
        user_id=user.id,
        card_number=request.data.get('card_number'),
        cvv=request.data.get('cvv'),
        expiration_date=request.data.get('expiration_date')
    )
    user.credit_cards.append(saved_card)


def handle_cash_payment(session, payment):
    if payment.payment_method == 'cash':
        # Perform any necessary actions for a cash payment, such as marking the payment as complete
        cash_payment = CashPayment(payment_id=payment.id)
        session.add(cash_payment)
        session.commit()
        payment.status = 'completed'
        # Add any additional steps needed for a cash payment, such as printing a receipt





