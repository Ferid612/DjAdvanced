from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..models import Category, ProductColor, ProductEntry, Product, ProductMaterial, ProductMeasureValue, Supplier


# @login_required
# @permission_required("manage_products")
@csrf_exempt
@require_http_methods(["POST"])
def create_product_template(request):
    """
    This function is used to add products to a specific category.
    It checks if a product with the same name already exists in the database and if so, it does not add it.
    Parameters:
        category_id (integer): The name of the category to add the products to.
        supplier_id (integer): The name of the supplier for the products.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', 'SKU', and 'description'.
    """

    data = request.data
    session = request.session

    category_id = data.get('category_id')
    supplier_id = data.get('supplier_id')
    product_list = data.get('product_list')

    if not (category_id and supplier_id and product_list):
        return JsonResponse(
            {
                'answer': 'category_id, supplier_id, and product_list are required fields'
            },
            status=400,
        )
    # Get or create supplier
    supplier = session.query(Supplier).get(supplier_id)

    if not supplier:
        return JsonResponse(
            {'answer': f'There is no Supplier id {supplier_id}'}, status=400
        )
    # Get the category
    category = session.query(Category).get(category_id)
    if not category:
        return JsonResponse(
            {'answer': f'There is no category id {category_id}'}, status=400
        )
    # Get the names of existing products
    existing_products = [p.name for p in session.query(Product.name).filter(
        Product.name.in_([p['name'] for p in product_list])).all()]

    # Filter out existing products from the product list
    new_products = [p for p in product_list if p['name']
                    not in existing_products]

    # Create a list of Product objects from the new products
    products_to_add = [Product(
        name=p['name'],
        description=p['description'],
        supplier_id=supplier_id,
        category_id=category_id,
    ) for p in new_products]

    # Add the new products to the session
    session.bulk_save_objects(products_to_add)

    return JsonResponse(
        {
            'existing_products': existing_products,
            'added_products': [p['name'] for p in new_products],
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def create_product_entry(request):
    """
    This function creates a new product entry with the given information.
    The function receives the following parameters from the request object:
    - product_id: the id of the product associated with the new entry
    - color_id: the id of the color of the product in the new entry
    - material_id: the id of the material of the product in the new entry
    - quantity: the quantity of the product in the new entry
    - SKU: the SKU code of the product in the new entry
    - price: the price of the product in the new entry
    - measures: a list of dictionaries, each representing a product measure associated with the new entry. Each dictionary
                should contain the keys "measure_id" (the id of the measure) and "value" (the value of the measure).

    If the product entry creation is successful, the function returns a JSON response with a success message and the new entry's information.
    If an error occurs during the creation process, the function returns a JSON response with an error message and the error details.
    """
    # Get the parameters from the request object
    data = request.data
    product_id = data.get('product_id')
    color_id = data.get('color_id')
    material_id = data.get('material_id')
    measure_value_id = data.get('measure_value_id')

    quantity = data.get('quantity')
    SKU = data.get('SKU')
    price = data.get('price')

    session = request.session
    # Check if the product with the given id exists
    product = session.query(Product).get(product_id)
    if not product:
        return JsonResponse(
            {'answer': f"Product with id {product_id} does not exist."},
            status=404,
        )
    # Check if the color with the given id exists
    color = session.query(ProductColor).get(color_id)
    if not color:
        return JsonResponse(
            {'answer': f"Color with id {color_id} does not exist."}, status=404
        )
    # Check if the material with the given id exists
    material = session.query(ProductMaterial).get(material_id)
    if not material:
        return JsonResponse(
            {'answer': f"Material with id {material_id} does not exist."},
            status=404,
        )
    # Check if the measure with the given id exists
    if measure_value_id:
        measure = session.query(ProductMeasureValue).get(measure_value_id)

        if not measure:
            return JsonResponse(
                {
                    'answer': f"Measure with id {measure_value_id} does not exist."
                },
                status=404,
            )
        new_entry = ProductEntry(product_id=product_id, measure_value_id=measure_value_id,
                                 color_id=color_id, material_id=material_id, quantity=quantity, SKU=SKU, price=price)
        print("NEASURE ADDING TO ENTRY")
    else:
        print("NEASURE NOT ADDING TO ENTRY")

        new_entry = ProductEntry(product_id=product_id, color_id=color_id,
                                 material_id=material_id, quantity=quantity, SKU=SKU, price=price)

    session.add(new_entry)
    session.commit()

    # Return a success message with the new entry information
    entry_info = {
        'id': new_entry.id,
        'product_id': new_entry.product_id,
        'color_id': new_entry.color_id,
        'material_id': new_entry.material_id,
        'measure_value_id': measure_value_id,
        'quantity': new_entry.quantity,
        'SKU': new_entry.SKU,
        'price': new_entry.price

    }
    return JsonResponse(
        {'answer': 'Product entry created successfully', 'entry': entry_info},
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def update_product(request):
    """
    This function is used to update an existing product in the database.
    Parameters:
        product_id (int): The id of the product to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'product' table, and the values should be the new values for each column.
    """

    data = request.data
    session = request.session

    product_id = data.get('product_id')
    new_values = data.get('new_values')

    if not product_id or not new_values:
        return JsonResponse(
            {'answer': 'product_id and new_values are required fields'},
            status=400,
        )
    # Get the product with the given id
    product = session.query(Product).get(product_id)
    if not product:
        return JsonResponse(
            {'answer': 'A product with the given id does not exist'},
            status=400,
        )
    # Update the values for each column in the product table
    not_allowed_columns = ['id']
    response_details = []
    # iterate through new_values
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():  # iterate through the columns in the new_value
            if column_name in not_allowed_columns:
                return JsonResponse(
                    {
                        'answer': f"Cannot update {column_name} through this endpoint."
                    },
                    status=400,
                )
            if column_name == "supplier_id":
                if supplier := session.query(Supplier).get(value):
                    product.supplier_id = supplier.id
                else:
                    response_details.append(f"{value} supplier does not exist")
                    print(f"{value} supplier does not exist")
                continue

            if column_name == "category_id":
                if category := session.query(Category).get(value):
                    product.category_id = category.id
                else:
                    response_details.append(f"{value} category does not exist")
                    print(f"{value} category does not exist")
                continue

            setattr(product, column_name, value)

    return JsonResponse(
        {
            'Success': 'The product has been successfully updated',
            "response_details": response_details,
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def update_product_entry(request, entry_id):
    """
    This function is used to update an existing product in the database.
    Parameters:
        product_id (int): The id of the product to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'product' table, and the values should be the new values for each column.
    """

    data = request.data
    session = request.session
    new_values = data.get('new_values')

    if not entry_id or not new_values:
        return JsonResponse(
            {'answer': 'entry_id and new_values are required fields'},
            status=400,
        )
    # Get the product_entry with the given id
    product_entry = session.query(ProductEntry).get(entry_id)
    if not product_entry:
        return JsonResponse(
            {'answer': 'A product_entry with the given id does not exist'},
            status=400,
        )
    # Update the values for each column in the product_entry table
    not_allowed_columns = ['id']
    response_details = []
    # iterate through new_values
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():  # iterate through the columns in the new_value
            if column_name in not_allowed_columns:
                return JsonResponse(
                    {
                        'answer': f"Cannot update {column_name} through this endpoint."
                    },
                    status=400,
                )
            setattr(product_entry, column_name, value)

    return JsonResponse(
        {
            'Success': 'The product has been successfully updated',
            "response_details": response_details,
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def delete_product(request):
    """
    This function is used to delete a specific product.
    Parameters:
        product_id (int): The ID of the product to be deleted.
    """

    data = request.data
    product_id = data.get('product_id')
    session = request.session

    product = session.query(Product).get(product_id)

    if not product:
        return JsonResponse(
            {'answer': f'No product found with product.id {product_id}'},
            status=404,
        )
    session.delete(product)

    return JsonResponse(
        {
            'message': f'Product with product.id {product_id} has been successfully deleted.'
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def delete_product_entry(request, entry_id):
    """
    This function is used to delete a specific product.
    Parameters:
        product_id (int): The ID of the product to be deleted.
    """

    data = request.data
    session = request.session

    product_entry = session.query(ProductEntry).get(entry_id)

    if not product_entry:
        return JsonResponse(
            {
                'answer': f'No product_entry found with product_entry.id {entry_id}'
            },
            status=404,
        )
    session.delete(product_entry)

    return JsonResponse(
        {
            'message': f'product_entry with product_entry.id {entry_id} has been successfully deleted.'
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST"])
def update_all_product_entries(request):
    """
    This function is used to update an existing product in the database.
    Parameters:
        product_id (int): The id of the product to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'product' table, and the values should be the new values for each column.
    """

    data = request.data
    session = request.session

    new_values = data.get('new_values')

    # Get the product with the given id
    product_entries = session.query(ProductEntry).all()

    # Update the values for each column in the product table
    not_allowed_columns = ['id']
    response_details = []
    for product_entry in product_entries:
        # iterate through new_values
        for index, new_value in enumerate(new_values):
            for column_name, value in new_value.items():  # iterate through the columns in the new_value
                if column_name in not_allowed_columns:
                    return JsonResponse(
                        {
                            'answer': f"Cannot update {column_name} through this endpoint."
                        },
                        status=400,
                    )
                setattr(product_entry, column_name, value)

    return JsonResponse(
        {
            'Success': 'The product has been successfully updated',
            "response_details": response_details,
        },
        status=200,
    )
