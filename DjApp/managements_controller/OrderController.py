from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.managements_controller.UserController import add_credit_card
from DjApp.models import CashPayment, CreditCard, CreditCardPayment, DiscountCoupon, DiscountCouponUser, Order, OrderItem, Payment
from ..helpers import GetErrorDetails, add_get_params
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
        user = request.person.user[0]
        shopping_session = user.shopping_session[0]
        cart_items_in_order = get_cart_items_in_order(shopping_session)
        new_order = create_order(session, user, cart_items_in_order)
        payment = create_payment(new_order, request)
        handle_credit_card_payment(payment, request)
        handle_cash_payment(session, payment)

        payment.status = 'completed'

        delete_items_from_cart(session, cart_items_in_order)
        session.commit()
        response = JsonResponse(
            {
                "answer": "The add_or_change cart item process successfully finished.",
                "order_details": new_order.to_json()
            },
            status=200
        )
        add_get_params(response)
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
    user = request.person.user[0]
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
