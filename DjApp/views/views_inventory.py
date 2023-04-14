from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse, redirect
from django.http import JsonResponse
from sqlalchemy import func
from DjApp.views.views_shopping import get_product_entry_price_after_discount
from DjApp.decorators import require_http_methods
from sqlalchemy.orm import joinedload
from ..models import Category, Product, ProductColor, ProductEntry, ProductMaterial, ProductMeasure, Supplier
from ..helpers import add_get_params
from typing import List
from sqlalchemy.orm import joinedload


def hello(request):
    return HttpResponse("Hello world")


@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_product(request, product_id,product_entry_id=None):
    """
    This function is used to retrieve the details of a specific product.
    Parameters:
        product_id (int): The id of the product to retrieve.
    """
    if product_entry_id:
        return redirect('get_product_entry', product_entry_id=product_entry_id)
    
    
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
    product_entries = []
    for entry in product.entries:
        size = None
        images = None
        rates_data = None
        rates = None
        if entry.rates:
            rates_data = entry.rates[0].get_raters_data(session,entry.id)
            rates = [{"rate_id":rate.id, "user_id":rate.user_id, "username":rate.user.person.username,"rate_comment":rate.rate_comment, "rate":rate.rate, "status":rate.status } for rate in entry.rates]
        if entry.size:
            size = {"size_id": entry.size.id, "size": entry.size.value, "size_type": entry.size.measure.name}
        
        if entry.images:
            images = [{"id": image.id, "url": image.image_url, "title": image.title, "entry_id":image.product_entry_id} for image in entry.images ]
            
        product_entries.append({
            "entry_id": entry.id,
            "price_prev": entry.price,
            "quantity": entry.quantity,
            "SKU": entry.SKU,
            "size": size,
            "images": images,
            "color": {"color_id": entry.color.id, "color_name": entry.color.name, "color_code": entry.color.color_code},
            "material": {"material_id": entry.material_id, "material_name": entry.material.name},
            'cargo_active': entry.cargo_active,
            "rates_data":rates_data,
            "rates":rates,
            
        })

    response = JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'supplier_data': {'supplier_id': product.supplier_id, 'supplier_name': product.supplier.name },
        'category_data': {'category_id': product.category_id, 'category_name': product.category.name },
        'product_enties': product_entries,
    }, status=200)

    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_entry_for_card(request, product_entry_id):
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


    # Get the product category chain
    image = None
    rates_data = None
    if entry.rates:
        rates_data = entry.rates[0].get_raters_data(session, entry.id)
      
    if entry.images:
        image = {"id": entry.images[0].id, "url": entry.images[0].image_url, "title": entry.images[0].title, "entry_id": entry.images[0].product_entry_id}


    exist_colors = entry.product.get_exist_colors(session)        
           
    product_current_price =  get_product_entry_price_after_discount(session, entry.id)
    
    response = JsonResponse({
        "entry_id": entry.id,
        "product_id": entry.product_id,
        "product_name": entry.product.name,
        "price_prev": entry.price,
        "price_current": product_current_price,
        "quantity": entry.quantity,
        "color": {"color_id": entry.color.id, "color_name": entry.color.name, "color_code": entry.color.color_code},
        "image": image,
        "rates_data": rates_data,
        "exist_colors":exist_colors,
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

    # Get the product category chain
    size = None
    images = None
    rates_data = None
    rates = None
    if entry.rates:
        rates_data = entry.rates[0].get_raters_data(session, entry.id)
        rates = [{"rate_id": rate.id, "user_id": rate.user_id, "username": rate.user.person.username,
                  "rate_comment": rate.rate_comment, "rate": rate.rate, "status": rate.status} for rate in entry.rates]
    if entry.size:
        size = {"size_id": entry.size.id, "size": entry.size.value, "size_type": entry.size.measure.name}

    if entry.images:
        images = [{"id": image.id, "url": image.image_url, "title": image.title, "entry_id": image.product_entry_id}
                  for image in entry.images]


    exist_colors = entry.product.get_exist_colors(session)        
    exist_materials = entry.product.get_exist_materials(session)        

    exist_sizes = None
    if entry.size:
        exist_sizes = entry.product.get_exist_sizes(session)        
        
    product_current_price =  get_product_entry_price_after_discount(session, entry.id)

    fags = entry.get_all_fags()

    comments = entry.get_entry_comments()
    
    response = JsonResponse({
        "entry_id": entry.id,
        "product_id": entry.product_id,
        "product_name": entry.product.name,
        "price_prev": entry.price,
        "price_current": product_current_price,
        "product_description": entry.product.description,
        "quantity": entry.quantity,
        "SKU": entry.SKU,
        "size": size,
        "color": {"color_id": entry.color.id, "color_name": entry.color.name, "color_code": entry.color.color_code},
        "material": {"material_id": entry.material_id, "material_name": entry.material.name},
        "supplier_data": {'supplier_id': entry.product.supplier_id,'supplier_name': entry.product.supplier.name },
        "category_data": {'category_id': entry.product.category_id, 'category_name': entry.product.category.name },
        "images": images,
        'cargo_active': entry.cargo_active,
        "rates_data": rates_data,
        "rates": rates,
        "fags": fags['fags_data'],
        "comments":comments['comment_tree'],
        "exist_colors":exist_colors,
        "exist_materials":exist_materials,
        "exist_sizes":exist_sizes,
    }, status=200)

    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_products_by_category(request,category_id, product_id=None):
    session = request.session
    
    
    if product_id:
        return redirect('get_product', product_id=product_id)


    
    # Query the category by name and retrieve all associated products
    category = session.query(Category).options(joinedload(Category.products)).get(category_id)
    products = [{'name': product.name, 'description': product.description} for product in category.products]

    response = JsonResponse({'category_id':category_id, 'products': products}, status=200)
    add_get_params(response)
    return  response



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_products_in_category(request,category_id, product_id=None):
    

    if product_id:
        return redirect('get_product', product_id=product_id)


    session = request.session    
    
    # Retrieve the parent category and its children recursively
    category = session.query(Category).options(joinedload(Category.products)).get(category_id)
    child_categories = category.get_child_categories()
    
    # Initialize a list to store all products in the parent category
    products = []
    
    # Recursively traverse through the category tree and retrieve all products
    def recursive_get_products(categories):
        for category in categories:
            if category.products:
                products.extend([{'id':product.id,
                                  'name': product.name,
                                  'description': product.description,
                                  'supplier_data': {'supplier_id':product.supplier_id, 'supplier_name':product.supplier.name },
                                  'category_data': {'category_id':product.category_id, 'category_name':product.category.name },
                                  }  for product in category.products])
            if category.has_children:
                child_categories = category.get_child_categories()
                recursive_get_products(child_categories)
                
    recursive_get_products(child_categories)
    
    response = JsonResponse({'category': category.name, 'products': products}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["GET"])
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
@require_http_methods(["GET","OPTIONS"])
def get_subcategory_categories(request, category_id):
    session = request.session
    category_name = request.data.get("category_name")

    # Query the category by name and retrieve its child categories
    category = session.query(Category).get(category_id)
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
def get_first_subcategory_categories(request,category_id):
    session = request.session
    
    # Query the category by name and retrieve its child categories
    category = session.query(Category).get(category_id)
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
        materials_data.append({"material_id": material.id, "material_name": material.name})

    # Retrieve all colors and their IDs and color codes
    colors = session.query(ProductColor).options(joinedload(ProductColor.product_entries)).all()
    for color in colors:
        colors_data.append({"color_id": color.id, "color_name": color.name, "color_code": color.color_code})

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
