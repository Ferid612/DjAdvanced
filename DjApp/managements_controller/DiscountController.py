from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from ..models import Discount, DiscountCoupon, DiscountCouponUser, ProductDiscount, ProductEntry, Users
from datetime import datetime, timedelta


@csrf_exempt
@require_http_methods(["POST", "GET"])
def create_discount(request):
    """
    This function handles discount creation by creating a new discount and adding it to the product.
    The function receives the following parameters from the request object:
    - name: the name of the discount
    - description: the description of the discount
    - discount_percent: the discount percentage
    - active: the status of the discount (active/inactive)
    If the discount creation is successful, the function returns a JSON response with a success message and the new discount's information.
    If an error occurs during the discount creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    data = request.data
    session = request.session

    discount_name = data.get('discount_name')
    discount_description = data.get('discount_description')
    discount_percent = data.get('discount_percent')
    active = data.get('active')

    active = active in ["True", True]

    if not (discount_name and discount_percent and active):
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. product_entry IDə, Name, Discount Percentage and Active status must be filled',
            },
            status=404,
        )
    # Check if have any discount for this name
    if (
        session.query(Discount).filter_by(name=discount_name).one_or_none()
    ):
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'The discount name already exists in this name.',
            },
            status=404,
        )
    # Create a new discount object with the given parameters
    new_discount = Discount(
        name=discount_name,
        description=discount_description,
        discount_percent=discount_percent,
        active=active,
    )

    # Add the new discount to the database and commit the changes
    session.add(new_discount)
    session.commit()
    return JsonResponse(
        {
            "Success": "The new discount has been successfully created.",
            "discount_detail": new_discount.to_json(),
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def discount_update(request):
    """
    This function updates an existing discount by its ID. The function receives the following parameters from the request object:
    - discount_id: the ID of the discount to be updated
    - name: the updated name of the discount
    - description: the updated description of the discount
    - discount_percent: the updated discount percentage
    - active: the updated status of the discount (active/inactive)
    If the update is successful, the function returns a JSON response with a success message and the updated discount's information.
    If an error occurs during the update process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    data = request.data
    session = request.session

    discount_id = data.get('discount_id')
    discount_name = data.get('name')
    discount_description = data.get('description')
    discount_percent = data.get('discount_percent')
    active = data.get('active')

    active = active in ["True", True]

    if not discount_id:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. Discount ID must be filled',
            },
            status=404,
        )
    # Check if the discount exists
    discount = session.query(Discount).get(discount_id)
    if not discount:
        return JsonResponse(
            {'answer': 'False', 'message': 'Discount not found'}, status=404
        )
    # Update the discount object with the given parameters
    if discount_name:
        discount.name = discount_name
    if discount_description:
        discount.description = discount_description
    if discount_percent:
        discount.discount_percent = discount_percent
    if active is not None:
        discount.active = active

    return JsonResponse(
        {
            'answer': 'The discount has been successfully updated.',
            'id': discount_id,
            'name': discount.name,
            'description': discount.description,
            'discount_percent': discount.discount_percent,
            'active': discount.active,
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def discount_delete(request, discount_id):
    """
    This function handles the deletion of a discount from a product.
    The function receives the discount ID from the request object and deletes the discount with that ID.
    If the discount deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the discount deletion process, the function returns a JSON response with an error message and the error details.
    """

    session = request.session

    if not discount_id:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. Discount name must be filled',
            },
            status=404,
        )
            # Start a new database session

    # Get the discount with the given ID
    discount = session.query(Discount).get(discount_id).first()

    if not discount:
        return JsonResponse(
            {'answer': 'False', 'message': 'Discount not found'}, status=404
        )
    # Delete the discount from the database and commit the changes
    session.delete(discount)

    return JsonResponse(
        {'Success': 'The discount has been successfully deleted.'}, status=200
    )


@csrf_exempt
@require_http_methods(["POST", "GET"])
def add_discount_to_products_by_ids(request):
    """
    This function adds the specified discount to the products with the specified IDs.
    The function receives the following parameters:
    - discount_id: the ID of the discount to add
    - product_emtries_ids: a list of product_entry IDəs to add the discount to
    If the discount is added to all the specified products successfully, the function returns a JSON response with a success message.
    If an error occurs during the discount addition process, the function returns a JSON response with an error message and the error details.
    """

    data = request.data
    session = request.session

    discount_id = data.get('discount_id')
    product_entries_ids = data.get('product_entries_ids')

    # Get the discount and the products from the database
    discount = session.query(Discount).get(discount_id)
    product_entries = session.query(ProductEntry).filter(
        ProductEntry.id.in_(product_entries_ids)).all()

    # Check if the discount and the products exist
    if not discount:
        return JsonResponse(
            {
                'Success': 'False',
                'message': 'The discount with the specified ID does not exist.',
            },
            status=404,
        )
    if not product_entries:
        return JsonResponse(
            {
                'Success': 'False',
                'message': 'None of the specified product_entry IDəs exist.',
            },
            status=404,
        )
    # Add the discount to the product_entries and commit the changes
    for product_entry in product_entries:
        product_discount = ProductDiscount(
            discount_id=discount.id, product_entry_id=product_entry.id)
        session.add(product_discount)

    return JsonResponse(
        {
            'Success': 'True',
            'message': 'The discount has been added to the specified products successfully.',
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def create_discount_coupon(request):
    """
    API endpoint to create a new discount coupon.
    The request should contain the following parameters:
    - code: the code for the discount coupon
    - discount: the discount amount for the coupon (in decimal form)
    - valid_from: the date and time the coupon becomes valid (in ISO format)
    - valid_to: the date and time the coupon expires (in ISO format)
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data

    # Get the parameters from the request
    code = data.get('code')
    discount = float(data.get('discount'))
    valid_from = datetime.fromisoformat(data.get('valid_from'))
    valid_to = datetime.fromisoformat(data.get('valid_to'))

    # Check if the coupon code already exists
    existing_coupon = session.query(
        DiscountCoupon).filter_by(code=code).first()
    if existing_coupon is not None:
        return JsonResponse({"error": "Coupon code already exists."}, status=400)

    # Check if the valid dates are valid
    now = datetime.now()
    if valid_from < now - timedelta(days=1):
        return JsonResponse({"error": "Valid from date must be at least one day in the future."}, status=400)
    if valid_to < valid_from:
        return JsonResponse({"error": "Valid to date must be after valid from date."}, status=400)

    # Create the discount coupon object
    discount_coupon = DiscountCoupon(
        code=code, discount=discount, valid_from=valid_from, valid_to=valid_to)

    session.add(discount_coupon)
    session.commit()

    return JsonResponse(
        {
            "answer": "Discount coupon created successfully.",
            "coupon": discount_coupon.to_json(),
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def update_discount_coupon(request, coupon_id):
    """
    API endpoint to update an existing discount coupon.
    The request should contain the following parameters:
    - code: the new code for the discount coupon (optional)
    - discount: the new discount amount for the coupon (in decimal form) (optional)
    - valid_from: the new date and time the coupon becomes valid (in ISO format) (optional)
    - valid_to: the new date and time the coupon expires (in ISO format) (optional)
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data

    # Get the discount coupon object to update
    discount_coupon = session.query(DiscountCoupon).get(coupon_id)
    if not discount_coupon:
        return JsonResponse({"error": "Discount coupon not found."}, status=404)

    # Update the discount coupon object
    discount_coupon.code = data.get('code', discount_coupon.code)
    discount_coupon.discount = float(
        data.get('discount', discount_coupon.discount))
    discount_coupon.valid_from = datetime.fromisoformat(
        data.get('valid_from', discount_coupon.valid_from.isoformat()))
    discount_coupon.valid_to = datetime.fromisoformat(
        data.get('valid_to', discount_coupon.valid_to.isoformat()))

    # Check if the valid dates are valid
    now = datetime.now()
    if discount_coupon.valid_from < now - timedelta(days=1):
        return JsonResponse({"error": "Valid from date must be at least one day in the future."}, status=400)
    if discount_coupon.valid_to < discount_coupon.valid_from:
        return JsonResponse({"error": "Valid to date must be after valid from date."}, status=400)

    session.commit()

    return JsonResponse(
        {
            "answer": "Discount coupon updated successfully.",
            "coupon": discount_coupon.to_json(),
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def delete_discount_coupon(request, coupon_id):
    """
    API endpoint to delete an existing discount coupon.
    """
    # Get the user object associated with the request
    session = request.session

    # Get the discount coupon object to delete
    discount_coupon = session.query(DiscountCoupon).get(coupon_id)
    if not discount_coupon:
        return JsonResponse({"error": "Discount coupon not found."}, status=404)

    # Delete the discount coupon object
    session.delete(discount_coupon)
    session.commit()

    return JsonResponse(
        {"answer": "Discount coupon deleted successfully."}, status=200
    )


@csrf_exempt
@require_http_methods(["POST"])
def assign_discount_coupon(request):
    """
    API endpoint to assign a discount coupon to a user.
    The request should contain the following parameters:
    - coupon_id: the ID of the discount coupon to assign
    - user_id: the ID of the user to assign the coupon to
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data

    # Get the parameters from the request
    coupon_code = data.get('code')
    user_id = data.get('user_id')

    # Check if the coupon and user exist
    coupon = session.query(DiscountCoupon).filter_by(code=coupon_code).first()
    if coupon is None:
        return JsonResponse({"error": "Discount coupon not found."}, status=404)

    user = session.query(Users).filter_by(id=user_id).first()
    if user is None:
        return JsonResponse({"error": "User not found."}, status=404)

    # Check if the valid dates are valid
    now = datetime.now()
    if coupon.valid_to < now:
        return JsonResponse({"error": "The coupon has expired."}, status=400)

    user_coupon = session.query(DiscountCouponUser).filter_by(
        user_id=user.id, discount_coupon_id=coupon.id).first()
    if user_coupon is not None:
        return JsonResponse({"error": "This coupon is already assign to this user."}, status=404)

    # Assign the coupon to the user
    user.discount_coupons.append(coupon)
    session.commit()

    return JsonResponse(
        {
            "answer": "Discount coupon assigned successfully.",
            "user_id": user_id,
            "coupon": coupon.to_json(),
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def unassign_discount_coupon(request):
    """
    API endpoint to unassign a discount coupon from a user.
    The request should contain the following parameters:
    - coupon_id: the ID of the discount coupon to unassign
    - user_id: the ID of the user to unassign the coupon from
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data

    # Get the parameters from the request
    coupon_id = data.get('coupon_id')
    user_id = data.get('user_id')

    # Check if the coupon and user exist
    coupon = session.query(DiscountCoupon).get(coupon_id)
    if coupon is None:
        return JsonResponse({"error": "Discount coupon not found."}, status=404)

    user = session.query(Users).get(user_id)
    if user is None:
        return JsonResponse({"error": "User not found."}, status=404)

    # Check if the coupon is assigned to the user
    if coupon not in user.discount_coupons:
        return JsonResponse({"error": "Discount coupon is not assigned to user."}, status=400)

    # Unassign the coupon from the user
    user.discount_coupons.remove(coupon)
    session.commit()

    return JsonResponse(
        {
            "answer": "Discount coupon unassigned successfully.",
            "coupon_id": coupon_id,
            "user_id": user_id,
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def activate_discount_coupon(request):
    """
    API endpoint to activate a discount coupon for a user.
    The request should contain the following parameters:
    - coupon_code: the code of the discount coupon to activate
    - user_id: the ID of the user to activate the coupon for
    """
    # Get the user object associated with the request
    session = request.session
    user = request.person.user[0]
    data = request.data

    # Get the parameters from the request
    coupon_code = data.get('code')

    # Check if the coupon and user exist
    coupon = session.query(DiscountCoupon).filter_by(code=coupon_code).first()
    if coupon is None:
        return JsonResponse({"error": "Discount coupon not found."}, status=404)

    # Deactivate any other coupons for the user

    active_coupon_users = session.query(DiscountCouponUser).filter(
        DiscountCouponUser.user_id == user.id,
        DiscountCouponUser.is_active == True).all()

    for active_coupon_user in active_coupon_users:
        if active_coupon_user.is_active:
            active_coupon_user.is_active = False

    # Activate the coupon for the user
    coupon_user = session.query(DiscountCouponUser).filter_by(
        user_id=user.id,
        discount_coupon_id=coupon.id
    ).first()
    if coupon_user is None:
        return JsonResponse({"error": "The coupon does not belong to this user."}, status=400)

    coupon_user.is_active = True
    session.commit()

    return JsonResponse(
        {
            "answer": "Discount coupon activated successfully.",
            "coupon_code": coupon_code,
            "user_id": user.id,
        },
        status=200,
    )
