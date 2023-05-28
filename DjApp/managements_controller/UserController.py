from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..models import CreditCard


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_credit_card(request):
    """
    This function is used to add a credit card to a user's account.
    It checks if a credit card with the same card number already exists for the user and if so, it does not add it.
    Parameters:
        user_id (integer): The ID of the user to add the credit card to.
        card_number (string): The card number of the credit card.
        expiration_date (string): The expiration date of the credit card.
        cvv (string): The CVV of the credit card.
    """

    data = request.data
    session = request.session
    user = request.person.user[0]

    card_number = data.get('card_number')
    expiration_date = data.get('expiration_date')
    cvv = data.get('cvv')

    if not (card_number and expiration_date and cvv):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    # check credit_card is exist
    if (
         session.query(CreditCard)
        .filter_by(user_id=user.id, card_number=card_number)
        .first()
    ):
        return JsonResponse(
            {
                'error': 'A credit card with the same card number already exists for this user'
            },
            status=409,
        )
    # Create a new CreditCard object for the user
    credit_card = CreditCard(
        user_id=user.id,
        card_number=card_number,
        expiration_date=expiration_date,
        cvv=cvv
    )

    # Add the new credit card to the session
    session.add(credit_card)
    session.commit()

    return JsonResponse(
        {'message': 'Credit card added successfully'}, status=201
    )


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
@login_required
def delete_credit_card(request, card_id):
    """
    This function is used to delete a credit card from a user's account.
    Parameters:
        card_id (integer): The ID of the credit card to be deleted.
    """

    session = request.session
    user = request.person.user[0]

    # Check if the credit card exists and belongs to the user
    credit_card = session.query(CreditCard).filter_by(
        id=card_id, user_id=user.id).first()

    if not credit_card:
        return JsonResponse(
            {
                'message': f'Credit card with ID {card_id} does not exist or does not belong to user ID {user.id}'
            },
            status=404,
        )
    # Delete the credit card
    session.delete(credit_card)
    session.commit()

    return JsonResponse(
        {
            'message': f'Credit card with ID {card_id} deleted for user ID {user.id}'
        },
        status=200,
    )
