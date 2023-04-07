from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from DjApp.decorators import require_http_methods
from sqlalchemy.orm import joinedload
from ..models import Category, Product, Supplier
from ..helpers import add_get_params
from typing import List


def hello(request):
    return HttpResponse("Hello world")


@csrf_exempt
@require_http_methods(["GET"])
def get_product(request):
    """
    This function is used to retrieve the details of a specific product.
    Parameters:
        product_id (int): The id of the product to retrieve.
    """
    
    product_id = request.data.get('product_id')
    
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
    category_chain = []
    category = product.category
    
    while category:
        category_chain.append({'id': category.id, 'name': category.name})
        category = category.parent
    
    # Create the response
    response = JsonResponse({'id': product.id,
                             'name': product.name,
                             'price': product.price,
                             'SKU': product.SKU,
                             'description': product.description,
                             'supplier_name': product.supplier.name,
                             'supplier_id': product.supplier.id,
                             'category_chain': category_chain[::-1]}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST","GET"])
def get_products_by_category(request):
    session = request.session
    category_name = request.data.get("category_name")
    
    # Query the category by name and retrieve all associated products
    category = session.query(Category).options(joinedload(Category.products)).filter_by(name=category_name).one()
    products = category.products

    response = JsonResponse({'category': category, 'products': products}, status=200)
    add_get_params(response)
    return  response





@csrf_exempt
@require_http_methods(["POST","GET"])
def get_categories(request):
    session = request.session
    categories = Category.get_root_categories(session)
    result = []

    for category in categories:
        category_dict = {"id": category.id, "name": category.name,"parent_id": category.parent_id}
        if category.has_children:
            child_categories = category.get_child_categories()
            category_dict["children"] = recursive_categories(child_categories)
        result.append(category_dict)

    return JsonResponse({"categories": result}, status=200)


def recursive_categories(categories):
    result = []
    for category in categories:
        category_dict = {"id": category.id, "name": category.name}
        if category.has_children:
            child_categories = category.get_child_categories()
            category_dict["children"] = recursive_categories(child_categories)
        result.append(category_dict)
    return result



@csrf_exempt
@require_http_methods(["POST","GET"])
def get_subcategory_categories(request):
    session = request.session
    category_name = request.data.get("category_name")

    # Query the category by name and retrieve its child categories
    category = session.query(Category).filter_by(name=category_name).first()
    if not category:
        return JsonResponse({'error': 'Category not found'}, status=404)

    child_categories = category.get_child_categories()
    result = []
    for child_category in child_categories:
        if not child_category.has_children:
            result.append({'name': child_category.name, 'id': child_category.id, 'parent_id': child_category.parent_id})
        else:
            subcategories = get_subcategory_categories(request, child_category.name)
            result += subcategories

    response = JsonResponse({'categories': result}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST","GET"])
def get_first_subcategory_categories(request):
    session = request.session
    category_name = request.data.get("category_name")

    # Query the category by name and retrieve its child categories
    category = session.query(Category).filter_by(name=category_name).first()
    if not category:
        return JsonResponse({'error': 'Category not found'}, status=404)

    child_categories = category.get_child_categories()
    result = []
    for child_category in child_categories:
        if not child_category.has_children:
            result.append({'name': child_category.name, 'id': child_category.id, 'parent_id': child_category.parent_id})
        else:
            first_subcategory = child_category.get_child_categories()[0]
            result.append({'name': first_subcategory.name, 'id': first_subcategory.id, 'parent_id': first_subcategory.parent_id})

    response = JsonResponse({'categories': result}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST","GET"])
def get_all_products_by_supplier_name(request):
    """
    This function returns all products that belong to a supplier by given supplier name.
    The supplier name is passed as a query parameter in the GET request.
    If the supplier does not exist, it returns a JSON response with an 'Is empty' message.
    If the supplier_name parameter is not provided in the GET request, it returns a JSON response with an 'answer' message.
    """
    # Get the supplier name from the GET request
    data = request.data
    session = request.session
    supplier_name = data.get('supplier_name')
    supplier_id = data.get('supplier_id')
    
    # Check if the supplier_name parameter was provided in the GET request
    if not (supplier_name or supplier_id):
       response = JsonResponse({'answer': 'supplier_name is a required parameter'}, status=400)
       add_get_params(response)    
       return response         
   
    supplier = session.query(Supplier).filter_by(name=supplier_name).one_or_none()
    supplier = supplier or session.query(Supplier).get(supplier_id)
    
    if not supplier:
        response = JsonResponse({'answer': 'Supplier does not exist'}, status=400)
        add_get_params(response)
        return response

    
    all_products = session.query(Product).filter_by(supplier_id=supplier.id).all()
    
    products_data = [product.to_json() for product in all_products]
    response = JsonResponse({f'{supplier.name} products': products_data}, status=200)
    add_get_params(response)
    return response
