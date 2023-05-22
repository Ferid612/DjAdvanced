from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import JsonResponse
from sqlalchemy import func
from DjApp.decorators import require_http_methods
from sqlalchemy.orm import joinedload
from ..models import Category, Product, ProductColor, ProductEntry, ProductMaterial, ProductMeasure, Supplier
from ..helpers import add_get_params
from typing import List


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_product(request, product_id, product_entry_id=None):
    """
    This function is used to retrieve the details of a specific product.
    Parameters:
        product_id (int): The id of the product to retrieve.
    """
    if product_entry_id:
        return redirect('product-entry-details', product_entry_id=product_entry_id)

    if not product_id:
        response = JsonResponse(
            {'answer': 'product_id is a required field'}, status=400)
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
        response = JsonResponse(
            {'answer': 'product_entry_id is a required field'}, status=400)
        add_get_params(response)
        return response

    # Get the product entry from the database
    session = request.session
    entry = session.query(ProductEntry).get(product_entry_id)

    if not entry:
        response = JsonResponse(
            {'answer': 'Product entry not found'}, status=404)
        add_get_params(response)
        return response

    response = JsonResponse({
        'product': entry.product.to_json(),
        'entry': entry.to_json(),
    }, status=200)

    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_entries(request, count=3, offset=0):
    """
    This function is used to retrieve the next 5 product entries from the database
    starting from the given offset.
    """
    session = request.session

    entries = session.query(ProductEntry).offset(offset).limit(count).all()

    # Convert each entry to a dictionary using list comprehension
    entry_dicts = [entry.to_json_for_card() for entry in entries]

    response = JsonResponse({'entries': entry_dicts}, status=200)
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
        response = JsonResponse(
            {'answer': 'product_entry_id is a required field'}, status=400)
        add_get_params(response)
        return response

    # Get the product entry from the database
    session = request.session

    entry = session.query(ProductEntry).get(product_entry_id)

    if not entry:
        response = JsonResponse(
            {'answer': 'Product entry not found'}, status=404)
        add_get_params(response)
        return response

    entry_card_data = entry.to_json_for_card()
    response = JsonResponse(entry_card_data, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_product_properties(request):
    """
    Get all materials, colors, and measures from the database and return them in a JSON response.

    Args:
        request: The incoming request object.

    Returns:
        A JsonResponse containing the retrieved materials, colors, and measures.
    """
    session = request.session
    measure_data = []
    # materials = session.query(ProductMaterial.id, ProductMaterial.name, func.count(ProductEntry.id)).outerjoin(ProductEntry.material).group_by(ProductMaterial.id).all()
    # materials_data = [{"material_id": material[0], "material_name": material[1], "num_entries": material[2]} for material in materials]

    # Retrieve all colors and their IDs and color codes
    materials = session.query(ProductMaterial).options(
        joinedload(ProductMaterial.product_entries)).all()
    materials_data = [material.to_json() for material in materials]
    # Retrieve all colors and their IDs and color codes
    colors = session.query(ProductColor).options(
        joinedload(ProductColor.product_entries)).all()
    colors_data = [color.to_json() for color in colors]
    # Retrieve all measures, their IDs, and their values
    measures = session.query(ProductMeasure).options(
        joinedload(ProductMeasure.values)).all()
    for measure in measures:
        values = [
            {"value_id": measure_value.id, "value": measure_value.value}
            for measure_value in measure.values
        ]
        measure_data.append(
            {"measure_id": measure.id, "measure_name": measure.name, "values": values})

    product_properties = {"materials_data": materials_data,
                          "colors_data": colors_data, "measure_data": measure_data}

    response = JsonResponse(product_properties, status=200)
    add_get_params(response)
    return response
