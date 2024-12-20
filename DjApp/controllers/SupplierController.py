from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjAdvanced.settings.production import PROFIL_IMAGE_ROOT
from DjApp.controllers.LocationController import create_address_object, update_object_address
from ..helpers import GetErrorDetails, save_uploaded_image
from ..models import PhoneNumber, ProfilImage, Supplier
from ..decorators import permission_required, login_required, require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def registration_of_supplier(request):
    """
    This function handles supplier registration by creating a new supplier account.
    The function receives the following parameters from the request object:
    - name: the name of the new supplier
    - location_id: the ID of the location where the supplier is located
    - phone_number: the phone number of the new supplier
    - description: the description of the supplier

    If the account creation is successful, the function returns a JSON response with a success message and the new supplier's information.
    If an error occurs during the account creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    data = request.data
    supplier_name = data.get('supplier_name')
    phone_number = data.get('phone_number')
    description = data.get('description')
    country_phone_code = data.get('country_phone_code')

    session = request.session
    # check exist supplier
    if (
        session.query(Supplier).filter_by(name=supplier_name).one_or_none()
    ):
        # If Supplier name already exists, return an error response
        return JsonResponse(
            {'answer': f"This supplier name '{supplier_name}' belongs to another supplier account."}, status=400)

        
        
    # check exist phone number
    if (
        session.query(PhoneNumber).filter_by(
            phone_number=phone_number).one_or_none()
    ):
        # If phone number already exists, return an error response
        return JsonResponse(
            {'answer': "This phone number belongs to another supplier account."}, status=400)

        
        

    # Create a new phone number object
    new_phone = PhoneNumber(
        phone_number=phone_number,
        country_phone_code=country_phone_code,
        phone_type_id=2
    )

    session.add(new_phone)
    session.commit()

    # Create a new supplier object
    new_supplier = Supplier(
        name=supplier_name,
        phone_number=new_phone,
        description=description
    )

    # Add the new supplier object to the database
    session.add(new_supplier)
    session.commit()

    # Return a success response
    return JsonResponse(
        {"answer": "The new supplier account has been successfully created.",
            "supplier": new_supplier.to_json(),
         },
        status=200
    )

    
    


@csrf_exempt
@require_http_methods(["POST"])
def update_profile_image(request):
    """
    This function handles adding or changing a supplier's profile image by receiving a file containing the new image.
    The function receives the following parameters from the request object:
    - image: the file containing the new image

    If the image upload is successful, the function returns a JSON response with a success message and the new user's updated information.
    If an error occurs during the image upload process, the function returns a JSON response with an error message and the error details.
    """
    # Get the parameters from the request object
    session = request.session

    image_file = request.FILES.get('image')
    image_title = request.data.get("image_title")
    supplier_id = request.data.get("supplier_id")

    supplier = session.query(Supplier).get(supplier_id)
    if not supplier:
        # If supplier not found
        return JsonResponse(
            {"error": "Supplier id is not correct."},
            status=400
        )

    
    if not image_file:
        # If no image file is provided, return an error response
        return JsonResponse(
            {"error": "No image file provided."},
            status=400
        )
        

        

    # Save the image file to the server
    path = PROFIL_IMAGE_ROOT / 'suppliers'
    image_path = save_uploaded_image(image_file, path)

    if (
        old_profil_image := session.query(ProfilImage)
        .filter_by(supplier_id=supplier.id)
        .one_or_none()
    ):
        session.delete(old_profil_image)
        session.commit()

    image_data = {
        "image_url": image_path,
        "title": image_title,
        "supplier_id": supplier.id
    }

    profil_image = ProfilImage(**image_data)
    # Commit the session to the database
    session.add(profil_image)
    session.commit()

    # Return a success response
    return JsonResponse(
        {"answer": "The profile image has been updated successfully.",
            "supplier_profil_image": image_data},
        status=200
    )

    
    


@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
def update_supplier_data(request):
    """
    Update an existing supplier in the database.

    Args:
        request: HttpRequest object representing the current request.

    Request Parameters:
        supplier_name (string): The name of the supplier to be updated.
        new_values (dict): A dictionary of the new values for the supplier. The keys in the dictionary should correspond to the names of the columns in the 'supplier' table, and the values should be the new values for each column.

    Returns:
        JsonResponse: A JSON response indicating whether the update was successful.

    Raises:
        ValueError: If the required request parameters are missing or invalid.
        PermissionDenied: If the requesting user does not have permission to update the specified supplier.
    """

    # Extract required parameters from the request
    data = request.data  # get the data from the request
    session = request.session  # get the session from the request
    # get the supplier_id from the data
    supplier_name = data.get('supplier_name')
    new_values = data.get('new_values')  # get the new_values from the data

    # Check that required parameters are present and valid
    if not supplier_name or not new_values:  # check if supplier_id and/or new_values are missing
        return JsonResponse(
            {'answer': 'supplier_name and new_values are required fields'}, status=400)
        
        

    # Get the supplier object from the database
    supplier = session.query(Supplier).filter_by(name=supplier_name).first()

    if not supplier:  # check if supplier object is found
        return JsonResponse(
            {'answer': f"Could not find supplier with name {supplier_name}"}, status=404)
        
        

    # Check if any of the disallowed columns are being updated
    # Update supplier object with new values
    # set of columns that cannot be updated through this endpoint
    not_allowed_columns = ['id', 'phone_number_id', 'location_id']
    for new_value in new_values:
        for column_name, value in new_value.items():
            if column_name in not_allowed_columns:  # check if the column is disallowed
                return JsonResponse(
                    {'answer': f"Cannot update {column_name} through this endpoint."}, status=400)
                
                

            # set the new value of the column in the supplier object
            setattr(supplier, column_name, value)

    return JsonResponse(
        {'success': f"Supplier with name {supplier_name} has been updated."}, status=200)
    
    


@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
def delete_supplier(request):
    """
    Delete a supplier from the database.

    Args:
        request: HttpRequest object representing the current request.

    Request Parameters:
        supplier_name (string): The name of the supplier to be deleted.

    Returns:
        JsonResponse: A JSON response indicating whether the deletion was successful.

    Raises:
        ValueError: If the required request parameters are missing or invalid.
        PermissionDenied: If the requesting user does not have permission to delete the specified supplier.
    """

    # Extract required parameters from the request
    supplier_name = request.data.get('supplier_name')
    session = request.session
    # Check that required parameters are present and valid
    if not supplier_name:
        return JsonResponse(
            {'answer': 'supplier_name is a required field'}, status=400)
        
        

    # Retrieve the supplier object from the database
    supplier = session.query(Supplier).filter_by(name=supplier_name).first()

    # Check if the supplier exists
    if not supplier:
        return JsonResponse(
            {'answer': f'Supplier {supplier_name} not found'}, status=404)
        
        

    # Delete the supplier from the database
    session.delete(supplier)

    # Return a success message
    return JsonResponse(
        {'success': 'Supplier {supplire_name} successfully deleted'}, status=200)
    
    


@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
def update_supplier_address(request):
    
    supplier_name = request.data.get("supplier_name")
    supplier = request.session.query(
        Supplier).filter_by(name=supplier_name).first()



    session = request.session
    data = request.data
    if supplier.location:
        address_obj = update_object_address(session, supplier.location, data)
    else:
        address_obj = create_address_object(session, data)
        
    supplier.location = address_obj
    session.commit()

    return JsonResponse(
        {'answer': 'The addres has been successfully applied to supplier',
         'supplier_id': supplier.id,
         'new_address_obj_json': address_obj.to_json(),
         }, status=200)
    
    
