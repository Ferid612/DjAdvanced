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
    print(category_id)
    if not category_id and not category_id == 0:
        response = JsonResponse({'error': 'Category id must be exist'}, status=404)
        add_get_params(response)
        return response
    
    
    # Query the category by ID and retrieve its child categories
    categories = []
    if category_id == 0:
        categories = session.query(Category).filter_by(parent_id=None).order_by(Category.id)        
    else:
        categories = session.query(Category).filter_by(parent_id=category_id).order_by(Category.id)
    
    
    if not categories:
        response =  JsonResponse({'error': 'Category not found'}, status=404)
        add_get_params(response)
        return response
            
    
    result = [category.to_json() for category in categories ]
    
    response = JsonResponse({'categories': result}, status=200)
    add_get_params(response)
    return response


