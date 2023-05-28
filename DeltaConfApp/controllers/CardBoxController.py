
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DeltaConfApp.models import CardBox, ProductEntryCardBox
from DjApp.models import ProductEntry
from DjApp.decorators import login_required, require_http_methods


@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
def create_card_box(request):
    """
    This function handles the creation of a new card box.
    The function receives the following parameters from the request object:
    - name: the name of the card box to be created
    - description: the description of the card box to be created
    If the card box creation is successful, the function returns a JSON response with a success message and the new card box's information.
    If an error occurs during the card box creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    name = request.data.get("name")
    description = request.data.get("description")
    session = request.session

    if not (name and description):
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. Name and description must be filled.',
            },
            status=404,
        )
    if card_box_exist := session.query(CardBox).filter_by(name=name).first():
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Card box with the given name already exists.',
            },
            status=404,
        )
    # Create a new card box object with the given parameters
    new_card_box = CardBox(
        name=name,
        description=description,
    )

    # Add the new card box to the database and commit the changes
    session.add(new_card_box)
    session.commit()

    return JsonResponse(
        {
            'Success': 'The new card box has been successfully created.',
            "card_box": new_card_box.to_json(),
        },
        status=200,
    )




@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
def update_card_box(request, pk):
    """
    This function handles updating a card box with the specified ID.
    The function receives the following parameters from the request object:
    - name: the updated name of the card box (optional)
    - description: the updated description of the card box (optional)
    If the update is successful, the function returns a JSON response with a success message and the updated card box's information.
    If an error occurs during the update process, the function returns a JSON response with an error message and the error details.
    """
    session = request.session

    # Retrieve the card box object to update
    card_box = session.query(CardBox).get(pk)

    if not card_box:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Card box with the given ID does not exist.',
            },
            status=404,
        )
    if name := request.data.get("name"):
        card_box.name = name

    if description := request.data.get("description"):
        card_box.description = description

    # Save the updated card box to the database and commit the changes
    session.add(card_box)
    session.commit()

    return JsonResponse(
        {
            'Success': 'The card box has been successfully updated.',
            'card_box': card_box.to_json(),
        },
        status=200,
    )



@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
def delete_card_box(request, pk):
    """
    This function handles the deletion of a card box from the database.
    The function receives the pk parameter from the URL and deletes the card box with the given ID.
    If the deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the deletion process, the function returns a JSON response with an error message and the error details.
    """

    # Get the card box with the given ID from the database
    session = request.session
    card_box = session.query(CardBox).get(pk)

    if not card_box:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Card box with the given ID does not exist.',
            },
            status=404,
        )
    try:
        # Delete the card box from the database and commit the changes
        session.delete(card_box)
        session.commit()

        return JsonResponse(
            {'Success': 'The card box has been successfully deleted.'},
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'An error occurred while deleting the card box.',
                'error_details': str(e),
            },
            status=500,
        )



@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
def add_product_entry_to_card_box(request, pk):
    """
    This function handles adding a product entry to a card box.
    The function receives the following parameters from the request object:
    - card_box_id: the ID of the card box to which the product entry should be added
    - product_entry_id: the ID of the product entry to be added
    If the product entry addition is successful, the function returns a JSON response with a success message and the updated card box's information.
    If an error occurs during the product entry addition process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object)
    product_entry_id = request.data.get("product_entry_id")
    session = request.session

    # Check if the card box with the given ID exists
    card_box = session.query(CardBox).get(pk)
    if not card_box:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Card box with the given ID does not exist.',
            },
            status=404,
        )
    # Check if the product entry with the given ID exists
    product_entry = session.query(ProductEntry).get(product_entry_id)
    if not product_entry:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Product entry with the given ID does not exist.',
            },
            status=404,
        )
    # Check if the card box already has the product entry
    if session.query(ProductEntryCardBox).filter_by(card_box_id=pk, product_entry_id=product_entry_id).first():
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'The card box already has the given product entry.',
            },
            status=400,
        )
    # Add the product entry to the card box
    product_entry_card_box = ProductEntryCardBox(
        card_box_id=pk,
        product_entry_id=product_entry_id
    )
    session.add(product_entry_card_box)
    session.commit()

    return JsonResponse(
        {
            'Success': 'The product entry has been successfully added to the card box.',
            'card_box': card_box.to_json_with_entries(session),
        },
        status=200,
    )



@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
def delete_product_entry_from_card_box(request, pk):
    """
    This function handles deleting a product entry from a card box.
    The function receives the following parameters from the request object:
    - card_box_id: the ID of the card box from which the product entry should be deleted
    - product_entry_id: the ID of the product entry to be deleted
    If the product entry deletion is successful, the function returns a JSON response with a success message and the updated card box's information.
    If an error occurs during the product entry deletion process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    session = request.session

    # Check if the card box has the product entry
    product_entry_card_box = session.query(ProductEntryCardBox).get(pk)
    if not product_entry_card_box:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'The card box does not have the given product entry.',
            },
            status=400,
        )
    # Remove the product entry from the card box
    session.delete(product_entry_card_box)
    session.commit()

    return JsonResponse(
        {
            'Success': 'The product entry has been successfully deleted from the card box.'
        },
        status=200,
    )



