from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from DjAdvanced.settings import  PROFIL_IMAGE_ROOT
from DjApp.managements_controller.LocationController import add_address_to_object, update_object_address
from ..helpers import GetErrorDetails, add_get_params, save_uploaded_image
from ..models import Country,  PhoneNumber, ProfilImage, Supplier
from ..decorators import permission_required, login_required, require_http_methods



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
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
    country_code = data.get('country_code')
    
    session = request.session

    # Query for the phone number object
    supplier = session.query(Supplier).filter_by(
        name=supplier_name).one_or_none()

    if supplier:
        # If Supplier name already exists, return an error response
        response = JsonResponse(
            {'answer': f"This supplier name '{supplier_name}' belongs to another supplier account."}, status=400)

        add_get_params(response)
        return response

    
    # Query for the phone number object
    phone = session.query(PhoneNumber).filter_by(
        phone_number=phone_number).one_or_none()

    if phone:
        # If phone number already exists, return an error response
        response = JsonResponse(
            {'answer': "This phone number belongs to another supplier account."}, status=400)

        add_get_params(response)
        return response

    # Create a new phone number object
    new_phone = PhoneNumber(
        phone_number=phone_number,
        country_code= country_code,
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
    response = JsonResponse(
        {"answer": "The new supplier account has been successfully created.",
            "supplier":new_supplier.to_json(),
            },
        status=200
    )

    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
def add_or_change_supplier_profile_image(request):
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
        response = JsonResponse(
            {"error": "Supplier id is not correct."},
            status=400
        )
        
        add_get_params(response)

        return response


    if not image_file:
        # If no image file is provided, return an error response
        response = JsonResponse(
            {"error": "No image file provided."},
            status=400
        )
        add_get_params(response)
        
        return response


    # Save the image file to the server
    path = PROFIL_IMAGE_ROOT / 'persons'
    image_path = save_uploaded_image(image_file, path)


    
    old_profil_image = session.query(ProfilImage).filter_by(supplier_id = supplier.id).one_or_none()
    if old_profil_image:
        session.delete(old_profil_image)
        session.commit()


    image_data = {
        "image_url" : image_path,                
        "title" : image_title,     
        "supplier_id" : supplier.id 
    }
    
    profil_image = ProfilImage(**image_data)                
    # Commit the session to the database
    session.add(profil_image)
    session.commit()


    # Return a success response
    response = JsonResponse(
        {"answer": "The profile image has been updated successfully.",
            "supplier_profil_image": image_data},
        status=200
    )

    add_get_params(response)
    return response



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
    supplier_name = data.get('supplier_name')  # get the supplier_id from the data
    new_values = data.get('new_values')  # get the new_values from the data

    # Check that required parameters are present and valid
    if not supplier_name or not new_values:  # check if supplier_id and/or new_values are missing
        response = JsonResponse(
            {'answer': 'supplier_name and new_values are required fields'}, status=400)
        add_get_params(response)
        return response

    # Get the supplier object from the database
    supplier = session.query(Supplier).filter_by(name=supplier_name).first()

    if not supplier:  # check if supplier object is found
        response = JsonResponse(
            {'answer': f"Could not find supplier with name {supplier_name}"}, status=404)
        add_get_params(response)
        return response


    # Check if any of the disallowed columns are being updated
    # Update supplier object with new values
    not_allowed_columns = ['id', 'phone_number_id', 'location_id']  # set of columns that cannot be updated through this endpoint
    for new_value in new_values:
        for column_name, value in new_value.items():
            if column_name in not_allowed_columns:  # check if the column is disallowed
                response = JsonResponse(
                    {'answer': f"Cannot update {column_name} through this endpoint."}, status=400)
                add_get_params(response)
                return response

            setattr(supplier, column_name, value)  # set the new value of the column in the supplier object

    
    response = JsonResponse(
        {'success': f"Supplier with name {supplier_name} has been updated."}, status=200)
    add_get_params(response)
    return response



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
        response = JsonResponse(
            {'answer': 'supplier_name is a required field'}, status=400)
        add_get_params(response)
        return response

    # Retrieve the supplier object from the database
    supplier = session.query(Supplier).filter_by(name=supplier_name).first()

    # Check if the supplier exists
    if not supplier:
        response = JsonResponse(
            {'answer': f'Supplier {supplier_name} not found'}, status=404)
        add_get_params(response)
        return response

    # Delete the supplier from the database
    session.delete(supplier)
    
    
    # Return a success message
    response = JsonResponse(
        {'success': 'Supplier {supplire_name} successfully deleted'}, status=200)
    add_get_params(response)
    return response





@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
def add_supplier_address(request):
    supplier_name = request.data.get("supplier_name")
    supplier = request.session.query(Supplier).filter_by(name=supplier_name).first() 
    resp = add_address_to_object(request,supplier)
    
    response = JsonResponse(
    {'answer':'The addres has been successfully applied to supplier', 'resp':resp}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required('manage_supplier')
def update_supplier_address(request):
    """
    This function is used to update an existing user_adres in the database.
    Parameters:
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'userAddres' table, and the values should be the new values for each column.
    """
    
    supplier_name = request.data.get("supplier_name")
    supplier = request.session.query(Supplier).filter_by(name=supplier_name).first() 
    resp = update_object_address(request,supplier)

    response = JsonResponse(
        {'Success': 'The person address has been successfully updated'}, status=200)
    add_get_params(response)
    return response


