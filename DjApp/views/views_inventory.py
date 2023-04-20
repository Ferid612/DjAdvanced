from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import JsonResponse
from sqlalchemy import func
from DjApp.decorators import require_http_methods
from sqlalchemy.orm import joinedload
from ..models import Category, Product, ProductColor, ProductEntry, ProductMaterial, ProductMeasure, Supplier
from ..helpers import add_get_params
from typing import List
from sqlalchemy.orm import joinedload



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_product(request, product_id,product_entry_id=None):
    """
    This function is used to retrieve the details of a specific product.
    Parameters:
        product_id (int): The id of the product to retrieve.
    """
    if product_entry_id:
        return redirect('product-entry-details', product_entry_id=product_entry_id)
    
    
    if not product_id:
        response = JsonResponse({'answer': 'product_id is a required field'}, status=400)
        add_get_params(response)
        return response


    # Get the product from the database
    session = request.session
    product = session.query(Product).get(product_id)

    if not product:
        response = JsonResponse({'answer': 'Product not found'}, status=404)
        add_get_params(response)
        return response
    # Get the product category chain
    response = JsonResponse({
        'product': product.to_json(),
        'product_entries': product.get_exist_entries(),
    }, status=200)

    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_product_entry(request, product_entry_id):
    """
    This function is used to retrieve the details of a specific product entry.
    Parameters:
        product_entry_id (int): The id of the product entry to retrieve.
    """
    if not product_entry_id:
        response = JsonResponse({'answer': 'product_entry_id is a required field'}, status=400)
        add_get_params(response)
        return response

    # Get the product entry from the database
    session = request.session
    entry = session.query(ProductEntry).get(product_entry_id)

    if not entry:
        response = JsonResponse({'answer': 'Product entry not found'}, status=404)
        add_get_params(response)
        return response


    response = JsonResponse({
        'product': entry.product.to_json_for_entry(),
        'entry': entry.to_json(),
    }, status=200)

    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_product_entry_for_card(request, product_entry_id):
    """
    This function is used to retrieve the details of a specific product entry.
    Parameters:
        product_entry_id (int): The id of the product entry to retrieve.
    """
    if not product_entry_id:
        response = JsonResponse({'answer': 'product_entry_id is a required field'}, status=400)
        add_get_params(response)
        return response

    # Get the product entry from the database
    session = request.session
    
    entry = session.query(ProductEntry).get(product_entry_id)

    if not entry:
        response = JsonResponse({'answer': 'Product entry not found'}, status=404)
        add_get_params(response)
        return response


    
    entry_card_data = entry.to_json_for_card()
    response = JsonResponse(entry_card_data, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_products_by_category(request,category_id, product_id=None, product_entry_id=None):
    session = request.session
    
    if product_entry_id:
        return redirect('product-entry-details', product_entry_id=product_entry_id)
    
    if product_id:
        return redirect('product', product_id=product_id)


    
    # Query the category by name and retrieve all associated products
    category = session.query(Category).get(category_id)
    if not category:
        return JsonResponse({'error': 'Category not found'}, status=404)
    
    products = category.get_self_products()

    response = JsonResponse({'category':category.to_json(), 'products': products}, status=200)
    add_get_params(response)
    return  response



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_products_in_category(request,category_id, product_id=None):
    

    if product_id:
        return redirect('product', product_id=product_id)


    session = request.session    
    
    # Retrieve the parent category and its children recursively
    category = session.query(Category).get(category_id)
    if not category:
        return JsonResponse({'error': 'Category not found'}, status=404)
    
    products = category.get_all_products()
    
    response = JsonResponse({'category':category.to_json(), 'products': products}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET"])
def get_categories(request):
    session = request.session
    categories = Category.get_root_categories(session)
    result = []

    for category in categories:
        category_dict = category.to_json()
        if category.has_children:
            child_categories = category.get_child_categories()
            category_dict["children"] = recursive_categories(child_categories)
        result.append(category_dict)

    return JsonResponse({"categories": result}, status=200)



def recursive_categories(categories):
    result = []
    for category in categories:
        category_dict = category.to_json()
        if category.has_children:
            child_categories = category.get_child_categories()
            category_dict["children"] = recursive_categories(child_categories)
        result.append(category_dict)
    return result



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_subcategory_categories(request, category_id):
    session = request.session

    # Query the category by name and retrieve its child categories
    category = session.query(Category).get(category_id)
    if not category:
        return JsonResponse({'error': 'Category not found'}, status=404)

    result = []
    stack = [category] # initialize stack with the root category
    while stack:
        current_category = stack.pop()
        child_categories = current_category.get_child_categories()
        for child_category in child_categories:
            if not child_category.has_children:
                result.append(child_category.to_json())
            else:
                stack.append(child_category)

    response = JsonResponse({'categories': result}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_first_subcategory_categories(request, category_id):
    session = request.session
    if not category_id:
        response = JsonResponse({'error': 'Category id must be exist'}, status=404)
        add_get_params(response)
        return response
    
    
    # Query the category by ID and retrieve its child categories
    if category_id == 0:
        categories = session.query(Category).filter_by(parent_id=None).all()        
    else:
        categories = session.query(Category).filter_by(parent_id=category_id)
    
    
    if not categories:
        response =  JsonResponse({'error': 'Category not found'}, status=404)
        add_get_params(response)
        return response
            
    
    result = [category.to_json() for category in categories ]
    
    response = JsonResponse({'categories': result}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_all_products_by_supplier(request,supplier_id):
    """
    This function returns all products that belong to a supplier by given supplier name.
    The supplier name is passed as a query parameter in the GET request.
    If the supplier does not exist, it returns a JSON response with an 'Is empty' message.
    If the supplier_name parameter is not provided in the GET request, it returns a JSON response with an 'answer' message.
    """
    # Get the supplier name from the GET request
    data = request.data
    session = request.session
    
    # Check if the supplier_name parameter was provided in the GET request
    if not supplier_id:
       response = JsonResponse({'answer': 'supplier_id is not a required parameter'}, status=400)
       add_get_params(response)    
       return response         
   
   
    supplier = session.query(Supplier).get(supplier_id)
    if not supplier:
        response = JsonResponse({'answer': 'Supplier does not exist'}, status=400)
        add_get_params(response)
        return response

    
    all_products = session.query(Product).filter_by(supplier_id=supplier_id).all()
    
    products_data = [product.to_json() for product in all_products]
    response = JsonResponse({f'{supplier.name} products': products_data}, status=200)
    add_get_params(response)
    return response





@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_product_properties(request):
    
    session = request.session 
    colors_data = []
    measure_data = []
    materials_data = []
  

    # materials = session.query(ProductMaterial.id, ProductMaterial.name, func.count(ProductEntry.id)).outerjoin(ProductEntry.material).group_by(ProductMaterial.id).all()
    # materials_data = [{"material_id": material[0], "material_name": material[1], "num_entries": material[2]} for material in materials]
    
    # Retrieve all colors and their IDs and color codes
    materials = session.query(ProductMaterial).options(joinedload(ProductMaterial.product_entries)).all()
    for material in materials:
        materials_data.append(material.to_json())

    # Retrieve all colors and their IDs and color codes
    colors = session.query(ProductColor).options(joinedload(ProductColor.product_entries)).all()
    for color in colors:
        colors_data.append(color.to_json())

    # Retrieve all measures, their IDs, and their values
    measures = session.query(ProductMeasure).options(joinedload(ProductMeasure.values)).all()
    for measure in measures:
        values = []
        for measure_value in measure.values:
            values.append({"value_id": measure_value.id, "value": measure_value.value})
        measure_data.append({"measure_id": measure.id, "measure_name": measure.name, "values": values})

    product_properties = {"materials_data": materials_data, "colors_data": colors_data, "measure_data": measure_data}
    
    response = JsonResponse(product_properties, status=200)
    add_get_params(response)
    return response
