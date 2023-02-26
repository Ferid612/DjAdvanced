from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from DjApp.decorators import login_required, require_http_methods
from ..models import Category, Subcategory, Product
from ..helpers import add_get_params, session_scope
import traceback, logging


def hello(request):
    return HttpResponse("Hello world")




@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
def get_all_products_by_subcategory_name(request):
    """
    This function returns all products that belong to a subcategory by given subcategory name.
    The subcategory name is passed as a query parameter in the GET request.
    If the subcategory does not exist, it returns a JSON response with an 'Is empty' message.
    If the subcategory_name parameter is not provided in the GET request, it returns a JSON response with an 'error' message.
    """
    # Get the subcategory name from the GET request
    data = request.data
    session = request.session
    subcategory_name = data.get('subcategory_name')
    
    # Check if the subcategory_name parameter was provided in the GET request
    if not subcategory_name:
        response = JsonResponse({'error': 'subcategory_name is a required parameter'}, status=400)


    # Try to find the subcategory by name in both the Category and Subcategory tables
    existing_category = (session.query(Category)
                        .filter_by(names=subcategory_name)
                        .one_or_none() or
                        session.query(Subcategory)
                        .filter_by(names=subcategory_name)
                        .one_or_none())

    if existing_category:
        all_products = (session.query(Product)
                        .filter_by(subcategory_id=existing_category.id)
                        .all())
        products_data = [{'name': product.name, 'description': product.description, 'price': product.price} for product in all_products]
        response = JsonResponse({'data': products_data}, status=200)
        add_get_params(response)
        return response
    else:
        response = JsonResponse({'data': 'Is empty'}, status=200)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
def get_products_by_category_name(request):
    """
    This function retrieves all products belonging to the subcategories under the specified category.
    :param request: HTTP request containing a query parameter 'category_name'
    :return: JsonResponse containing a list of products data in the 'data' key, or an error message if category does not exist
    """
    
    data = request.data
    session = request.session
    category_name = data.get('category_name')
    
    if not category_name:
        response = JsonResponse({'error': 'category_name is a required parameter'}, status=400)
        add_get_params(response)
        return response

    # Get the category object
    category = session.query(Category).filter_by(name=category_name).first()
    if not category:
        response = JsonResponse({'error': f"{category_name} does not exist in the category table."}, status=404)
        add_get_params(response)
        return response

    # Get the ids of all subcategories under the specified category
    subcategory_ids = (session.query(Subcategory.id)
                        .filter_by(category_id=category.id)
                        .all())
    subcategory_ids = [id[0] for id in subcategory_ids]
    # Get all products that belong to the subcategories with the retrieved ids
    products = (session.query(Product)
                .filter(Product.subcategory_id.in_(subcategory_ids))
                .all())
    products_data = [{'name': product.name, 'description': product.description, 'price': product.price} for product in products]

    response = JsonResponse({'data': products_data}, status=200)
    add_get_params(response)
    return response
        


@csrf_exempt
@require_http_methods(["POST","GET"])
@login_required
def get_categories_and_subcategories(request):
    """
    This function retrieves all categories and their subcategories.
    
    :return: list of dictionaries, each representing a category and its subcategories
    """
    session = request.session
    categories = session.query(Category).all()
    
    categories_data = []
    for category in categories:
        subcategories = session.query(Subcategory).filter(Subcategory.category_id == category.id).all()
        subcategories_data = [{'name': subcategory.name} for subcategory in subcategories]
        categories_data.append({'category': category.name, 'subcategories': subcategories_data})
    response = JsonResponse({'data': categories_data}, status=200)
    add_get_params(response)
    return response