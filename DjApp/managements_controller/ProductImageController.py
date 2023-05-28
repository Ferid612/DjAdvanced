import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from DjAdvanced.settings.production import MEDIA_ROOT, engine
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import GetErrorDetails, save_uploaded_image
from ..models import ProductEntry, ProductImage


@csrf_exempt
@require_http_methods(["POST"])
def add_product_image(request, entry_id):
    """
    This function handles the addition of a new image to a product.
    The function receives the following parameters from the request object:
    - product_id: the ID of the product to which the image should be added
    - image_url: the URL of the image to be added
    - title: the title of the image to be added
    If the image addition is successful, the function returns a JSON response with a success message and the new image's information.
    If an error occurs during the image addition process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object

        session = request.session
        image_title = request.data.get("image_title")
        image_url = request.data.get("image_url")
        image_index = request.data.get('index')
        image_file = request.FILES.get('image')

        if not (entry_id or image_file):
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'Missing data error. Product ID, Image URL and Title must be filled',
                },
                status=404,
            )
        # Check if the product exists
        product_entry = session.query(ProductEntry).get(entry_id)

        if not product_entry:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'ProductEntry with the given ID does not exist',
                },
                status=404,
            )
        if not image_url:

            # Check if the folder for the product images exists, and create it if it doesn't
            folder_path = MEDIA_ROOT / 'product_images' / product_entry.product.supplier.name
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            image_path = save_uploaded_image(image_file, folder_path)
        else:
            image_path = image_url

        # Create a new image object with the given parameters
        if not image_index and image_index != 0:
            image_index = 999

        new_image = ProductImage(
            product_entry_id=entry_id,
            image_url=image_path,
            title=image_title,
            index=image_index
        )

        # Add the new image to the database and commit the changes
        session.add(new_image)
        session.commit()
        return JsonResponse(
            {
                "Success": "The new image has been successfully added to the product.",
                'image': new_image.to_json(),
            },
            status=200,
        )
    except Exception as e:
        return GetErrorDetails(
            "Something went wrong when adding the image to the product.",
            e,
            404,
        )


@csrf_exempt
@require_http_methods(["POST"])
def add_image_to_all_product_entries(request):
    """
    This function handles the addition of a new image to all product entries.
    The function receives the following parameters from the request object:
    - image_url: the URL of the image to be added
    - title: the title of the image to be added
    If the image addition is successful, the function returns a JSON response with a success message and the new image's information.
    If an error occurs during the image addition process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object

        session = request.session
        image_title = request.data.get("image_title")
        image_url = request.data.get("image_url")
        image_file = request.FILES.get('image')

        if not image_file and not image_url:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'Missing data error. Image URL and Title must be filled',
                },
                status=404,
            )
        # Get all product entries
        product_entries = session.query(ProductEntry).all()

        # Check if there are any product entries
        if not product_entries:
            return JsonResponse(
                {'answer': 'False', 'message': 'No product entries found.'},
                status=404,
            )
        # Check if the folder for the product images exists, and create it if it doesn't
        if not image_url:
            supplier_name = product_entries[0].product.supplier.name
            folder_path = MEDIA_ROOT / 'product_images' / supplier_name
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Add the new image to all product entries
        for product_entry in product_entries:

            # Create a new image object with the given parameters
            new_image = ProductImage(
                product_entry_id=product_entry.id,
                image_url=image_url or save_uploaded_image(
                                              image_file, folder_path),
                title=image_title
            )

            # Add the new image to the database and commit the changes
            session.add(new_image)
            session.commit()

        return JsonResponse(
            {
                "Success": "The new image has been successfully added to all product entries."
            },
            status=200,
        )
    except Exception as e:
        return GetErrorDetails(
            "Something went wrong when adding the image to the product entries.",
            e,
            404,
        )


@csrf_exempt
@require_http_methods(["POST"])
def update_product_image(request, image_id):
    """
    This function handles updating a product image by changing its title and/or image URL.
    The function receives the following parameters from the request object:
    - image_id: the ID of the product image to update
    - title: the new title of the product image (optional)
    - image_url: the new URL of the product image (optional)
    If the update is successful, the function returns a JSON response with a success message and the updated product image's information.
    If an error occurs during the update process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        session = request.session
        title = data.get('title')
        image_url = data.get('image_url')
        image_index = request.data.get('index')

        if not image_id:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'Missing data error. Please provide an image ID.',
                },
                status=404,
            )
        # Get the product image object with the given ID
        product_image = session.query(ProductImage).get(image_id)

        if not product_image:

            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'Invalid image ID. No product image was found with the given ID.',
                },
                status=404,
            )
        # Update the product image's title and/or image URL if new values are provided
        if title:
            product_image.title = title
        if image_url:
            product_image.image_url = image_url
        if image_index:
            product_image.index = image_index

        return JsonResponse(
            {
                'Success': 'The product image has been successfully updated.',
                'image': product_image.to_json(),
            },
            status=200,
        )
    except Exception as e:
        return GetErrorDetails(
            'Something went wrong when updating the product image.', e, 404
        )


@csrf_exempt
@require_http_methods(["POST", "GET"])
def delete_product_image(request, image_id):
    """
    Deletes a product image from the database.
    The function receives the following parameters from the request object:
    - image_id: the ID of the image to be deleted.
    If the image deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the image deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the image ID from the request object
        data = request.data
        session = request.session

        if not image_id:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'Missing data error. Please provide the ID of the image you want to delete.',
                },
                status=404,
            )
        # Get the image object from the database
        image = session.query(ProductImage).get(image_id)

        if not image:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': 'The image with the specified ID does not exist in the database.',
                },
                status=404,
            )
        # Delete the image from the database and commit the changes
        session.delete(image)

        return JsonResponse(
            {"Success": "The image has been successfully deleted."}, status=200
        )
    except Exception as e:
        return GetErrorDetails(
            "Something went wrong when deleting the image.", e, 404
        )
