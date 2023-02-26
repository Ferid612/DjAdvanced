from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from ..models import  Discount, Product, ProductDiscount


@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
@permission_required("Manage discounts")
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

    discount_name = data.get('name')
    discount_description = data.get('description') 
    discount_percent = data.get('discount_percent') 
    active = data.get('active') 
    
    
    
    if not (discount_name and discount_percent and active):
        response = JsonResponse({'answer':'False', 'message':'Missing data error. Product ID, Name, Discount Percentage and Active status must be filled'}, status=404)            
        add_get_params(response)
        return response
    
    
    # Create a new discount object with the given parameters
    new_discount = Discount(
                            name=discount_name,
                            description=discount_description,
                            discount_percent=discount_percent,
                            active=active,
                            )
    
    # Add the new discount to the database and commit the changes
    session.add(new_discount)
    
    # Return a JSON response with a success message and the new discount's information
    response = JsonResponse({"Success":"The new discount has been successfully created.", "name": discount_name, "description": discount_description, "discount_percent": discount_percent, "active": active}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
@permission_required("Manage discounts")
def add_discount_to_products(request):
    """
    This function adds the specified discount to the products with the specified IDs.
    The function receives the following parameters:
    - discount_id: the ID of the discount to add
    - product_ids: a list of product IDs to add the discount to
    If the discount is added to all the specified products successfully, the function returns a JSON response with a success message.
    If an error occurs during the discount addition process, the function returns a JSON response with an error message and the error details.
    """
    

    data = request.data
    session = request.session

    product_names = data.getlist('product_names') 
    discount_name = data.get('name')
    
    # Get the discount and the products from the database
    discount = session.query(Discount).filter_by(name=discount_name).first()
    products = session.query(Product).filter(Product.name.in_(product_names)).all()
    
    # Check if the discount and the products exist
    if not discount:
        response = JsonResponse({'Success':'False', 'message':'The discount with the specified ID does not exist.'}, status=404)            
        add_get_params(response)
        return response
    
    if not products:
        response = JsonResponse({'Success':'False', 'message':'None of the specified product IDs exist.'}, status=404)            
        add_get_params(response)
        return response
    
    # Add the discount to the products and commit the changes
    for product in products:
        product_discount = ProductDiscount(discount_id=discount.id, product_id=product.id)
        session.add(product_discount)


    # Return a JSON response with a success message
    response = JsonResponse({'Success':'True', 'message':'The discount has been added to the specified products successfully.'}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage discounts")
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

    if not discount_id:
        response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Discount ID must be filled'}, status=404)
        add_get_params(response)
        return response



    # Check if the discount exists
    discount = session.query(Discount).filter_by(id=discount_id).first()
    if not discount:
        response = JsonResponse({'answer': 'False', 'message': 'Discount not found'}, status=404)
        add_get_params(response)
        return response

    # Update the discount object with the given parameters
    if discount_name:
        discount.name = discount_name
    if discount_description:
        discount.description = discount_description
    if discount_percent:
        discount.discount_percent = discount_percent
    if active is not None:
        discount.active = active


    # Return a JSON response with a success message and the updated discount's information
    response = JsonResponse({
        'answer': 'True',
        'message': 'The discount has been successfully updated.',
        'id': discount_id,
        'name': discount.name,
        'description': discount.description,
        'discount_percent': discount.discount_percent,
        'active': discount.active
    }, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage discounts")
def discount_delete(request):
    """
    This function handles the deletion of a discount from a product.
    The function receives the discount ID from the request object and deletes the discount with that ID.
    If the discount deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the discount deletion process, the function returns a JSON response with an error message and the error details.
    """
    
    # Get the discount ID from the request object
    discount_name = request.data.get('discount_name')
    session = request.session

    if not discount_name:
        response = JsonResponse({'answer':'False', 'message':'Missing data error. Discount name must be filled'}, status=404)            
        add_get_params(response)
        return response
    
        # Start a new database session

    # Get the discount with the given ID
    discount = session.query(Discount).filter_by(name=discount_name).first()
    
    if not discount:
        response = JsonResponse({'answer':'False', 'message':'Discount not found'}, status=404)            
        add_get_params(response)
        return response
    
    # Delete the discount from the database and commit the changes
    session.delete(discount)

    # Return a JSON response with a success message
    response = JsonResponse({'Success': 'The discount has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response


