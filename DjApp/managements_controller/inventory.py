import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sqlalchemy import DECIMAL, Boolean, DateTime, Float, Column, ForeignKey, Integer, String
import json

from DjAdvanced.settings import MEDIA_ROOT, engine
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import GetErrorDetails, add_get_params, save_uploaded_image 
from ..models import Base , Category, ProductColor, ProductEntry, ProductImage, Product, ProductMeasure,ProductMaterial, ProductMeasureValue, Supplier



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("Manage whole database")
def add_column_to_table(request):
    """This function adds a new column to a table in the database.

    Args:
        table_name (str): The name of the table.
        column_name (str): The name of the new column.
        column_type (str): The type of the new column.
        foreign_key (str, optional): The name of the foreign key table, if the new column is a foreign key. Defaults to None.

    Returns:
        JsonResponse: A JSON response indicating that the column has been added successfully.
    """
    data = request.data
    table_name = data.get('table_name')
    column_name = data.get('column_name')
    column_type = data.get('column_type')
    foreign_key = data.get('foreign_key')

    # Map the string values to the correct SQLAlchemy types
    type_map = {
        'Boolean':Boolean,
        'Decimal':DECIMAL,
        'Integer': Integer,
        'String': String,
        'Float': Float,
        'DateTime': DateTime,
    }

    # Get the SQLAlchemy type based on the string value
    column_type = type_map.get(column_type, String)

    # Checking if the new column is a foreign key or not.
    if foreign_key:
        column = Column(column_name, column_type, ForeignKey(foreign_key))
    else:
        column = Column(column_name, column_type)

    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    # adding new column
    try:
            
        engine.execute('ALTER TABLE %s ADD COLUMN %s %s' %
                    (table_name, column_name, column_type))
    except Exception as e:
        response =  GetErrorDetails("Something went wrong at execution time.",e,500)
        add_get_params(response)
        return response
        
    response = JsonResponse({'message': 'Column added successfully.'}, status=200)
    add_get_params(response)
    return response
        



@csrf_exempt
@require_http_methods(["POST"])
def add_category(request):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    data = request.data
    categories = data.get('categories')

    added_categories = []
    existing_categories = []

    session = request.session
    for category in categories:
        existing_category = session.query(Category).filter_by(name=category).one_or_none()

        # check if a category with the same name already exists
        if existing_category:
            existing_categories.append(category)
        else:
            new_category = Category(name=category)
            added_categories.append(category)
            session.add(new_category)  # add the new category to the session
            session.commit()    # commit the changes to the database

    response = JsonResponse({'existing_categories': existing_categories, 'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("Manage product categories")
def add_subcategories(request,category_id):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    data = request.data
    subcategories = data.get('subcategories')

    session = request.session

    # check if the parent category exists
    parent_category = session.query(Category).get(category_id)
    if not parent_category:
        response = JsonResponse({'message': f"Parent category '{category_id}' id does not exist"}, status=400)
        add_get_params(response)
        return response

    added_categories = []
    existing_categories = []

    for subcategory in subcategories:
        # check if the child category already exists
        existing_category = session.query(Category).filter_by(name=subcategory).one_or_none()
        if existing_category:
            existing_categories.append(subcategory)
        else:
            new_category = Category(name=subcategory, parent_id=parent_category.id)
            added_categories.append(subcategory)
            session.add(new_category)

    session.commit()  # commit all changes to the database

    response = JsonResponse({'existing_categories': existing_categories, 'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def add_measure(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    measure_name = request.data.get('measure_name')
    session = request.session
    new_measure = ProductMeasure.add_measure(session,measure_name) 

    print(new_measure.name)
    
    response = JsonResponse({'answer': "success"}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def add_measure_values(request,measure_id):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data
    
    values = data.get('values')
    product_measure = session.query(ProductMeasure).get(measure_id)
    
    for value in values:
        product_measure.append_value(session,value)
    
    
    response = JsonResponse({'answer': "success"}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def add_color(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data
    name = data.get('name')
    color_code = data.get('color_code')
    if not name or not color_code:
        response = JsonResponse({'message': 'Please provide a name and a color code'}, status=400)
        add_get_params(response)
        return response
    color = ProductColor.add_color(session, name=name, color_code=color_code)
    
    
    response = JsonResponse({"color":color.to_json(),'answer': "success"}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
def add_material(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data
    name = data.get('name')
    
    material = ProductMaterial.add_material(session, name=name)
    
    
    response = JsonResponse({"color":material.to_json(),'answer': "success"}, status=200)
    add_get_params(response)
    return response



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
        response = JsonResponse({'answer': 'category_id, supplier_id, and product_list are required fields'}, status=400)
        add_get_params(response)
        return response

    # Get or create supplier
    supplier = session.query(Supplier).get(supplier_id)

    if not supplier:
        response = JsonResponse({'answer': f'There is no Supplier id {supplier_id}'}, status=400)
        add_get_params(response)
        return response

    # Get the category
    category = session.query(Category).get(category_id)
    if not category:
        response = JsonResponse({'answer': f'There is no category id {category_id}'}, status=400)
        add_get_params(response)
        return response

    # Get the names of existing products
    existing_products = [p.name for p in session.query(Product.name).filter(
        Product.name.in_([p['name'] for p in product_list])).all()]

    # Filter out existing products from the product list
    new_products = [p for p in product_list if p['name'] not in existing_products]

    # Create a list of Product objects from the new products
    products_to_add = [Product(
        name = p['name'],
        description = p['description'],
        supplier_id = supplier_id,
        category_id = category_id,
    ) for p in new_products]

    # Add the new products to the session
    session.bulk_save_objects(products_to_add)

    # Create the response
    response = JsonResponse({'existing_products': existing_products, 'added_products': [p['name'] for p in new_products]},
                            status=200)
    add_get_params(response)
    return response



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
        response = JsonResponse({'answer': f"Product with id {product_id} does not exist."}, status=404)
        add_get_params(response)
        return response

    # Check if the color with the given id exists
    color = session.query(ProductColor).get(color_id)
    if not color:
        response = JsonResponse({'answer': f"Color with id {color_id} does not exist."}, status=404)
        add_get_params(response)
        return response

    # Check if the material with the given id exists
    material = session.query(ProductMaterial).get(material_id)
    if not material:
        response = JsonResponse({'answer': f"Material with id {material_id} does not exist."}, status=404)
        add_get_params(response)
        return response

    # Check if the SKU code is already in use
    entry_with_sku = session.query(ProductEntry).filter_by(SKU=SKU).one_or_none()
    if entry_with_sku:
        response = JsonResponse({'answer': f"A product entry with SKU {SKU} already exists."}, status=400)
        add_get_params(response)
        return response



    # Create the new product entry
    


    # Check if the measure with the given id exists
    if measure_value_id:
        measure = session.query(ProductMeasureValue).get(measure_value_id)

        if not measure:
            response = JsonResponse({'answer': f"Measure with id {measure_value_id} does not exist."}, status=404)
            add_get_params(response)
            return response
        
        new_entry = ProductEntry(product_id=product_id, measure_value_id=measure_value_id, color_id=color_id, material_id=material_id, quantity=quantity, SKU=SKU, price=price)
        print("NEASURE ADDING TO ENTRY")
    else:
        print("NEASURE NOT ADDING TO ENTRY")
        
        new_entry = ProductEntry(product_id=product_id, color_id=color_id, material_id=material_id, quantity=quantity, SKU=SKU, price=price)

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
    response = JsonResponse({'answer': 'Product entry created successfully', 'entry': entry_info}, status=201)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
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
        response = JsonResponse({'answer': 'product_id and new_values are required fields'}, status=400)
        add_get_params(response)
        return response
    
    # Get the product with the given id
    product = session.query(Product).get(product_id)
    if not product:
        response = JsonResponse({'answer': 'A product with the given id does not exist'}, status=400)
        add_get_params(response)
        return response
    
    # Update the values for each column in the product table
    not_allowed_columns = ['id']
    response_details = []
    for index, new_value in enumerate(new_values): # iterate through new_values
        for column_name, value in new_value.items(): # iterate through the columns in the new_value
            if column_name in not_allowed_columns:
                response = JsonResponse({'answer': f"Cannot update {column_name} through this endpoint."}, status=400)
                add_get_params(response)
                return response
            
            if column_name == "supplier_id":
                supplier = session.query(Supplier).get(value)
                if not supplier:
                    response_details.append(f"{value} supplier does not exist")
                    print(f"{value} supplier does not exist")
                else:
                    product.supplier_id = supplier.id
                continue
            
            if column_name == "category_id":
                category = session.query(Category).get(value)
                if not category:
                    response_details.append(f"{value} category does not exist")
                    print(f"{value} category does not exist")
                else:
                    product.category_id = category.id
                continue
                    
            setattr(product, column_name, value)

    response = JsonResponse({'Success': 'The product has been successfully updated',"response_details":response_details}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
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
        response = JsonResponse({'answer': f'No product found with product.id {product_id}'}, status=404)
        add_get_params(response)
        return response
    session.delete(product)
    

    response = JsonResponse({'message': f'Product with product.id {product_id} has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
def add_product_image(request, product_entry_id):
    """
    This function handles the addition of a new image to a product.
    The function receives the following parameters from the request object:
    - product_id: the ID of the product to which the image should be added
    - image_url: the URL of the image to be added
    - title: the title of the image to be added
    If the image addition is successful, the function returns a JSON response with a success message and the new image's information.
    If an error occurs during the image addition process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object

        session = request.session
        image_title = request.data.get("image_title")
        image_url = request.data.get("image_url")
        image_file = request.FILES.get('image')
        
    
        if not (product_entry_id or image_file ):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Product ID, Image URL and Title must be filled'}, status=404)
            add_get_params(response)
            return response

        
        # Check if the product exists
        product_entry = session.query(ProductEntry).get(product_entry_id)
        
        if not product_entry:
            response = JsonResponse({'answer':'False', 'message':'ProductEntry with the given ID does not exist'}, status=404)
            add_get_params(response)
            return response

        if not image_url:
                
            # Check if the folder for the product images exists, and create it if it doesn't
            folder_path = MEDIA_ROOT / 'product_images' / product_entry.product.supplier.name
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            image_path = save_uploaded_image(image_file, folder_path)
        else:
            image_path = image_url
        
        # Create a new image object with the given parameters
        new_image = ProductImage(
            product_entry_id=product_entry_id,
            image_url=image_path,
            title=image_title
        )
        
        # Add the new image to the database and commit the changes
        session.add(new_image)
        session.commit()
        # Return a JSON response with a success message and the new image's information
        response = JsonResponse({"Success":"The new image has been successfully added to the product.", "product_id": product_entry_id, "image_url": image_path, "title": image_title}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding the image to the product.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
def update_product_image(request, image_id):
    """
    This function handles updating a product image by changing its title and/or image URL.
    The function receives the following parameters from the request object:
    - image_id: the ID of the product image to update
    - title: the new title of the product image (optional)
    - image_url: the new URL of the product image (optional)
    If the update is successful, the function returns a JSON response with a success message and the updated product image's information.
    If an error occurs during the update process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        session = request.session
        title = data.get('title')
        image_url = data.get('image_url')

        if not image_id:
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Please provide an image ID.'}, status=404)
            add_get_params(response)
            return response
    


        # Get the product image object with the given ID
        product_image = session.query(ProductImage).get(image_id)

        if not product_image:

            response = JsonResponse({'answer': 'False', 'message': 'Invalid image ID. No product image was found with the given ID.'}, status=404)
            add_get_params(response)
            return response

        # Update the product image's title and/or image URL if new values are provided
        if title:
            product_image.title = title
        if image_url:
            product_image.image_url = image_url

           
        # Return a JSON response with a success message and the updated product image's information
        response = JsonResponse({'Success': 'The product image has been successfully updated.', 'id': product_image.id, 'product_id': product_image.product_id, 'title': product_image.title, 'image_url': product_image.image_url}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when updating the product image.', e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST","GET"])
# @login_required
# @permission_required("manage_products")
def delete_product_image(request, image_id):
    """
    Deletes a product image from the database.
    The function receives the following parameters from the request object:
    - image_id: the ID of the image to be deleted.
    If the image deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the image deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the image ID from the request object
        data = request.data
        session = request.session
        
        
        if not image_id:
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Please provide the ID of the image you want to delete.'}, status=404)            
            add_get_params(response)
            return response


        # Get the image object from the database
        image = session.query(ProductImage).get(image_id)
        
        if not image:
            response = JsonResponse({'answer':'False', 'message':'The image with the specified ID does not exist in the database.'}, status=404)
            add_get_params(response)
            return response
    
        # Delete the image from the database and commit the changes
        session.delete(image)
    
        
        # Return a JSON response with a success message
        response = JsonResponse({"Success":"The image has been successfully deleted."}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when deleting the image.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("GOD MODE")
def delete_all_tables(request):
    """ 
    This function deletes all tables.
    """
    user="Farid@!@"
    if user == "Farid":    
        Base.metadata.drop_all(bind=engine,checkfirst=True)
        response = JsonResponse({"message":"Deleted all tables succesfully."},status=200)
        add_get_params(response)
        return response
    else:
        response = JsonResponse({"message":"User is not admin."},status=200)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST", "GET"])
# @login_required
# @permission_required("manage_products")
def delete_null_category_products(request):
    """
    This function deletes all products that have a null category_id.
    """
    session = request.session
    # query to get all products that have a null category_id
    null_category_products = session.query(
        Product).filter(Product.category_id == None).all()
    # Iterate through the products and delete them one by one
    for product in null_category_products:
        session.delete(product)
        session.commit()
        print(
            f"Deleted {len(null_category_products)} products with null category_id")
        # Return the number of deleted products for confirmation
        
    response = JsonResponse({"message":"deleted all products that have a null category_id succesfully.", "lentgth of null_category_products": len(null_category_products)},status=200)
    add_get_params(response)
    return response

