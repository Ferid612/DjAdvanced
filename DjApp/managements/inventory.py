from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from sqlalchemy import DECIMAL, Boolean, DateTime, Float, Column, ForeignKey, Integer, String
import json

from DjAdvanced.settings import engine
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import GetErrorDetails, add_get_params, session_scope
from ..models import Base , Category, ProductImage, Subcategory, Product, Supplier



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage whole database")
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
@login_required
@permission_required("Manage product categories")
def add_category(request):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    data = request.data
    categories = data.getlist('categories')

    added_categories = []
    existing_categories = []
    with session_scope(engine) as session:
        for category in categories:
            existing_category = session.query(Category).filter_by(name=category).one_or_none()
            existing_subcategory = session.query(Subcategory).filter_by(name=category).one_or_none()

            # check if a category or subcategory with the same name already exists
            if existing_category or existing_subcategory:
                existing_categories.append(category)
            else:
                new_category = Category(name=category)
                added_categories.append(category)
                session.add(new_category)  # add the new category to the session
        session.commit()  # commit the changes to the database

    response = JsonResponse({'existing_categories': existing_categories, 'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response        



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("Manage product categories")
def add_subcategory(request):
    """
    This function adds new subcategories to the given parent category or subcategory.
    It first checks if the subcategory or category with the same name already exists,
    and if it does, it won't add it.
    :param parent_name: the name of the parent category or subcategory
    :type parent_name: str
    :param new_subcategories: the names of the subcategories to be added
    :type new_subcategories: list
    """
    # Get parent name and new subcategories from the request
    
    
    data = request.data
    parent_name = data.get('parent_name')
    new_subcategories = data.get('new_subcategories')

    
    # Create a session for database operations


    # Lists to keep track of existing and added subcategories
    existing_categories = []
    added_categories = []

    existing_categories = [c.name for c in session.query(Subcategory.name).filter(Subcategory.name.in_(new_subcategories)).union(session.query(Category.name).filter(Category.name.in_(new_subcategories))).all()]
    added_categories = [s for s in new_subcategories if s not in existing_categories]
    
    with session_scope(engine) as session:
        sub_parent = session.query(Subcategory).filter_by(name=parent_name).one_or_none()
        parent = session.query(Category).filter_by(name=parent_name).one_or_none()

    if not ( parent and sub_parent):
        return JsonResponse({'error': f"Parent {parent_name} does not exist."}, status=400)

    elif sub_parent:
        new_subcategories = [{'name': s, 'category_id': sub_parent.category_id , 'parent_id': sub_parent.id} for s in added_categories]
    
    elif parent:
        new_subcategories = [{'name': s, 'category_id': parent.id } for s in added_categories]

    
    # Insert the new subcategories into the database
    try:
        session.bulk_insert_mappings(Subcategory, new_subcategories)
        session.commit()
    except Exception as e:
        session.rollback()

        response = GetErrorDetails("'Error adding subcategories.", e, 404)
        add_get_params(response)
        return response

    # Return a json response with the existing and added subcategories
    response = JsonResponse({'existing_categories': existing_categories, 'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("manage_products")
def add_products(request):
    """
    This function is used to add products to a specific subcategory.
    It checks if a product with the same name already exists in the database and if so, it does not add it.
    Parameters:
        subcategory_name (str): The name of the subcategory to add the products to.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', and 'description'.
    """
    
    data = request.data
    session = request.session
    
    subcategory_name = data.get('subcategory_name')
    supplier_name = data.get('supplier_name')
    product_list = data.get('product_list')

    
    if not (subcategory_name and product_list):
        response = JsonResponse({'error': 'subcategory_name and product_list are required fields'}, status=400)
        add_get_params(response)
        return response


        # Get or create supplier
    supplier = session.query(Supplier).filter_by(name=supplier_name).one_or_none()

    if not supplier:
        response = JsonResponse({'error': f'There is no Supplier named {supplier_name}'}, status=400)
        add_get_params(response)
        return response

    subcategory = session.query(Subcategory).filter_by(name=subcategory_name).one_or_none()
    if not subcategory:
        response = JsonResponse({'error': f'There is no sub_category named {subcategory_name}'}, status=400)
        add_get_params(response)
        return response
    

    # Get the names of existing products
    existing_products = [p.name for p in session.query(Product.name).filter(
        Product.name.in_([p['name'] for p in product_list])).all()]

    # Filter out existing products from the product list
    new_products = [p for p in product_list if p['name'] not in existing_products]


    # Create a list of Product objects from the new products
    products_to_add = [Product(
                            name=p['name'],
                            price=p['price'],
                            SKU=p['SKU'],
                            description=p['description'],
                            supplier=supplier, 
                            supplier_id=supplier.id, 
                            subcategory=subcategory,
                            subcategory_id=subcategory.id,
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
@login_required
@permission_required("manage_products")
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
        response = JsonResponse({'error': 'product_id and new_values are required fields'}, status=400)
        add_get_params(response)
        return response
    
    # Get the product with the given id
    product = session.query(Product).get(product_id)
    if not product:
        response = JsonResponse({'error': 'A product with the given id does not exist'}, status=400)
        add_get_params(response)
        return response
    
    
    # Update the values for each column in the product table
    not_allowed_columns = ['id']
    response_details = []
    for index, new_value in enumerate(new_values): # iterate through new_values
        for column_name, value in new_value.items(): # iterate through the columns in the new_value
            if column_name in not_allowed_columns:
                response = JsonResponse({'error': f"Cannot update {column_name} through this endpoint."}, status=400)
                add_get_params(response)
                return response
            if column_name == "supplier_name":
                supplier = session.query(Supplier).filter_by(name=value).one_or_none()
                if not supplier:
                    response_details.append(f"{value} supplier does not exist")
                    print(f"{value} supplier does not exist")
                else:
                    product.supplier_id = supplier.id
                continue
            
            if column_name == "subcategory_name":
                subcategory = session.query(Subcategory).filter_by(name=value).one_or_none()
                if not subcategory:
                    response_details.append(f"{value} subcategory does not exist")
                    print(f"{value} subcategory does not exist")
                else:
                    product.subcategory_id = subcategory.id
                continue
                    
            setattr(product, column_name, value)



    response = JsonResponse({'Success': 'The product has been successfully updated',"response_details":response_details}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("manage_products")
def delete_product(request):
    """
    This function is used to delete a specific product.
    Parameters:
        product_id (int): The ID of the product to be deleted.
    """

    

    data = request.data
    product_name = data.get('product_name')
    session = request.session
    
    product = session.query(Product).filter_by(name=product_name).first()

    if not product:
        response = JsonResponse({'error': f'No product found with product.name {product_name}'}, status=404)
        add_get_params(response)
        return response
    session.delete(product)
    

    response = JsonResponse({'message': f'Product with product.name {product_name} has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("manage_products")
def add_product_image(request):
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

        data = request.data
        product_id = data.get('product_id')
        image_url = data.get('image_url')
        title = data.get('title')
        session = request.session
        
        if not (product_id and image_url and title):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Product ID, Image URL and Title must be filled'}, status=404)
            add_get_params(response)
            return response



        
        # Check if the product exists
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            response = JsonResponse({'answer':'False', 'message':'Product with the given ID does not exist'}, status=404)
            add_get_params(response)
            return response
        
        # Create a new image object with the given parameters
        new_image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            title=title
        )
        
        # Add the new image to the database and commit the changes
        session.add(new_image)
    
        # Return a JSON response with a success message and the new image's information
        response = JsonResponse({"Success":"The new image has been successfully added to the product.", "product_id": product_id, "image_url": image_url, "title": title}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding the image to the product.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
@permission_required("manage_products")
def update_product_image(request):
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
        image_id = data.get('image_id')
        title = data.get('title')
        image_url = data.get('image_url')

        if not image_id:
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Please provide an image ID.'}, status=404)
            add_get_params(response)
            return response
    


        # Get the product image object with the given ID
        product_image = session.query(ProductImage).filter_by(id=image_id).first()

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
@require_http_methods(["POST"])
@login_required
@permission_required("manage_products")
def delete_product_image(request):
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
        
        image_id = data.get('image_id')
        
        if not image_id:
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Please provide the ID of the image you want to delete.'}, status=404)            
            add_get_params(response)
            return response

        # Get the image object from the database
        image = session.query(ProductImage).filter_by(id=image_id).first()
        
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
    user="Farid"
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
@require_http_methods(["POST"])
@login_required
@permission_required("Manage product categories")
def delete_null_category_subcategories(request):
    """
    This function deletes all subcategories that have a null category_id.
    """
    session = request.session


    # query to get all products that have a null subcategory_id
    null_category_subcategories = session.query(
        Subcategory).filter(Subcategory.category_id == None).all()
    # Iterate through the products and delete them one by one
    for category in null_category_subcategories:
        session.delete(category)
        print(
            f"Deleted {len(null_category_subcategories)} products with null subcategory_id")
        # Return the number of deleted products for confirmation
        
    response = JsonResponse({"message":"deleted all subcategories that have a null category_id succesfully.", "length_of_null_category_subcategories": len(null_category_subcategories)},status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST", "GET"])
@login_required
@permission_required("manage_products")
def delete_null_subcategory_products(request):
    """
    This function deletes all products that have a null subcategory_id.
    """
    session = request.session
    # query to get all products that have a null subcategory_id
    null_subcategory_products = session.query(
        Product).filter(Product.subcategory_id == None).all()
    # Iterate through the products and delete them one by one
    for product in null_subcategory_products:
        session.delete(product)
        session.commit()
        print(
            f"Deleted {len(null_subcategory_products)} products with null subcategory_id")
        # Return the number of deleted products for confirmation
        
    response = JsonResponse({"message":"deleted all products that have a null subcategory_id succesfully.", "lentgth of null_subcategory_products": len(null_subcategory_products)},status=200)
    add_get_params(response)
    return response

