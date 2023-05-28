from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjApp.decorators import login_required, permission_required, require_http_methods
from DjApp.models import Discount, DiscountCoupon


@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_all_discounts(request):
    """
    Retrieve all discounts from the database.

    Args:
        request: HttpRequest object representing the current request.

    Returns:
        JsonResponse: A JSON response containing a list of all discounts.
    """

    session = request.session

    discounts = session.query(Discount).all()

    discounts_json = [discount.to_json() for discount in discounts]

    return JsonResponse(discounts_json, safe=False)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_all_discount_coupons(request):
    """
    Retrieve all discount coupons from the database.

    Args:
        request: HttpRequest object representing the current request.

    Returns:
        JsonResponse: A JSON response containing a list of all discount coupons.
    """

    session = request.session

    discount_coupons = session.query(DiscountCoupon).all()

    coupons_json = [coupon.to_json() for coupon in discount_coupons]

    return JsonResponse(coupons_json, safe=False)


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_user_discount_coupons(request):
    """
    This function handles the retrieval of all the discount coupons associated with a user.
    The function receives the following parameters from the request object:
    - user_id: the ID of the user for which to retrieve the discount coupons
    If the retrieval is successful, the function returns a JSON response with a success message and the discount coupons's information.
    If an error occurs during the retrieval process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    user = request.person.user[0]

    discount_coupons = user.get_user_discount_coupons()

    return JsonResponse(
        {
            'Success': 'The user discount coupons have been successfully retrieved.',
            'user_id': user.id,
            "discount_coupons": discount_coupons,
        },
        status=200,
    )
