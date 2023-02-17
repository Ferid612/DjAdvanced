import datetime
import json
from django.http import JsonResponse
from sqlalchemy import DECIMAL, Boolean, DateTime, Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import  sessionmaker,subqueryload
from sqlalchemy.orm.exc import NoResultFound
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, token_required
from DjApp.helpers import GetErrorDetails, add_get_params
from .models import Base , Category, Discount, ProductDiscount, ProductImage, Subcategory, Product, Supplier
from DjAdvanced.settings import engine



@csrf_exempt
@token_required
@permission_required(permission_name="Manage whole database")
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
    table_name = request.POST.get('table_name')
    column_name = request.POST.get('column_name')
    column_type = request.POST.get('column_type')
    foreign_key = request.POST.get('foreign_key')

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
def add_category(request):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    session = sessionmaker(bind=engine)()
    
    categories = request.POST.getlist('categories')

    added_categories = []
    existing_categories = []
    for category in categories:
        print("category")
        existing_category = session.query(Category).filter_by(name=category).one_or_none()
        existing_subcategory = session.query(Subcategory).filter_by(name=category).one_or_none()

        # check if a category or subcategory with the same name already exists
        if existing_category or existing_subcategory:
            print(f"{category} already exists")
            existing_categories.append(category)

        else:
            new_category = Category(name=category)
            added_categories.append(category)
            session.add(new_category)  # add the new category to the session
   
        session.commit()  # commit the changes to the database


    response = JsonResponse({'existing_categories': existing_categories,'added_categories':added_categories}, status=200)
    add_get_params(response)
    return response
        



@csrf_exempt
# @token_required
# @permission_required(permission_name="Manage product categories")
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
    
    
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        parent_name = data.get('parent_name')
        new_subcategories = data.get('new_subcategories')

    else:    
        parent_name = request.POST.get('parent_name')
        new_subcategories = request.POST.getlist('new_subcategories')

    # Create a session for database operations
    session = sessionmaker(bind=engine)()

    # Lists to keep track of existing and added subcategories
    existing_categories = []
    added_categories = []

    existing_categories = [c.name for c in session.query(Subcategory.name).filter(Subcategory.name.in_(new_subcategories)).union(session.query(Category.name).filter(Category.name.in_(new_subcategories))).all()]
    added_categories = [s for s in new_subcategories if s not in existing_categories]
    
    sub_parent = session.query(Subcategory).filter_by(name=parent_name).one_or_none()
    parent = session.query(Category).filter_by(name=parent_name).one_or_none()

    if not ( parent or sub_parent):
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




# @token_required
# @permission_required(permission_name="Manage products")
@csrf_exempt
def add_products(request):
    """
    This function is used to add products to a specific subcategory.
    It checks if a product with the same name already exists in the database and if so, it does not add it.
    Parameters:
        subcategory_name (str): The name of the subcategory to add the products to.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', and 'description'.
    """
    
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        subcategory_name = data.get('subcategory_name')
        supplier_name = data.get('supplier_name')
        product_list = data.get('product_list')
    
    else:    
        subcategory_name = request.POST.get('subcategory_name')
        supplier_name = request.POST.get('supplier_name')
        product_list = request.POST.getlist('product_list')
    
    
    
    if not (subcategory_name and product_list):
        response = JsonResponse({'error': 'subcategory_name and product_list are required fields'}, status=400)
        add_get_params(response)
        return response

    session = sessionmaker(bind=engine)()



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
                            subcategory=subcategory,
                            ) for p in new_products]

    # Add the new products to the session
    session.bulk_save_objects(products_to_add)

    # Commit the changes to the database
    session.commit()

    # Create the response
    response = JsonResponse({'existing_products': existing_products, 'added_products': [p['name'] for p in new_products]},
                            status=200)
    add_get_params(response)
    return response



@csrf_exempt
@token_required
@permission_required(permission_name="Manage products")
def update_product(request):
    """
    This function is used to update an existing product in the database.
    Parameters:
        product_id (int): The id of the product to be updated.
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'product' table, and the values should be the new values for each column.
    """
    product_name = request.POST.get('product_name')
    new_values = request.POST.get('new_values')
    if not product_name or not new_values:
        response = JsonResponse({'error': 'product_id and new_values are required fields'}, status=400)
        add_get_params(response)
        return response
    
    session = sessionmaker(bind=engine)()


    # Get the product with the given id
    product = session.query(Product).filter_by(name=product_name).one_or_none()
    if not product:
        response = JsonResponse({'error': 'A product with the given id does not exist'}, status=400)
        add_get_params(response)
        return response
    
    # Update the values for each column in the product table
    for column_name, new_value in new_values.items():
        setattr(product, column_name, new_value)

    # Commit the changes to the database
    session.commit()
    response = JsonResponse({'Success': 'The product has been successfully updated'}, status=200)



@csrf_exempt
@token_required
@permission_required(permission_name="Manage products")
def delete_product(request):
    """
    This function is used to delete a specific product.
    Parameters:
        product_id (int): The ID of the product to be deleted.
    """
    session = sessionmaker(bind=engine)()

    product_name = request.POST.get('product_name')
    
    product = session.query(Product).filter_by(name=product_name).first()
    
    if not product:
        response = JsonResponse({'error': f'No product found with product.name {product_name}'}, status=404)
        add_get_params(response)
        return response
    session.delete(product)
    session.commit()
    
    response = JsonResponse({'message': f'Product with product.name {product_name} has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@token_required
@permission_required(permission_name="Manage products")
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
        product_id = request.POST.get('product_id')
        image_url = request.POST.get('image_url')
        title = request.POST.get('title')
        
        if not (product_id and image_url and title):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Product ID, Image URL and Title must be filled'}, status=404)
            add_get_params(response)
            return response
        
        session = sessionmaker(bind=engine)() # Start a new database session
        
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
        session.commit()
        session.close()
        
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
@token_required
@permission_required(permission_name="Manage products")
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
        image_id = request.POST.get('image_id')
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')

        if not image_id:
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Please provide an image ID.'}, status=404)
            add_get_params(response)
            return response

        session = sessionmaker(bind=engine)() # Start a new database session

        # Get the product image object with the given ID
        product_image = session.query(ProductImage).filter_by(id=image_id).first()

        if not product_image:
            session.close()
            response = JsonResponse({'answer': 'False', 'message': 'Invalid image ID. No product image was found with the given ID.'}, status=404)
            add_get_params(response)
            return response

        # Update the product image's title and/or image URL if new values are provided
        if title:
            product_image.title = title
        if image_url:
            product_image.image_url = image_url

        # Commit the changes and close the session
        session.commit()
        session.close()

        # Return a JSON response with a success message and the updated product image's information
        response = JsonResponse({'Success': 'The product image has been successfully updated.', 'id': product_image.id, 'product_id': product_image.product_id, 'title': product_image.title, 'image_url': product_image.image_url}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when updating the product image.', e, 404)
        add_get_params(response)
        return response



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
        image_id = request.POST.get('image_id')
        
        if not image_id:
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Please provide the ID of the image you want to delete.'}, status=404)            
            add_get_params(response)
            return response
        
        session = sessionmaker(bind=engine)() # Start a new database session
        
        # Get the image object from the database
        image = session.query(ProductImage).filter_by(id=image_id).first()
        
        if not image:
            response = JsonResponse({'answer':'False', 'message':'The image with the specified ID does not exist in the database.'}, status=404)
            add_get_params(response)
            return response
        
        # Delete the image from the database and commit the changes
        session.delete(image)
        session.commit()
        session.close()
        
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
@token_required
@permission_required(permission_name="Manage discounts")
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
    try:
        
        # Get the parameters from the request object
        discount_name = request.POST.get('name')
        discount_description = request.POST.get('description') 
        discount_percent = request.POST.get('discount_percent') 
        active = request.POST.get('active') 
        
        
        
        if not (discount_name or discount_percent or active):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Product ID, Name, Discount Percentage and Active status must be filled'}, status=404)            
            add_get_params(response)
            return response
        
        session = sessionmaker(bind=engine)() # Start a new database session
        
        # Create a new discount object with the given parameters
        new_discount = Discount(
                                name=discount_name,
                                description=discount_description,
                                discount_percent=discount_percent,
                                active=active,
                                )
        
        # Add the new discount to the database and commit the changes
        session.add(new_discount)
        session.commit()
        session.close()
        
        # Return a JSON response with a success message and the new discount's information
        response = JsonResponse({"Success":"The new discount has been successfully created.", "name": discount_name, "description": discount_description, "discount_percent": discount_percent, "active": active}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding the discount.", e, 404)
        add_get_params(response)
        return response




@csrf_exempt
@token_required
@permission_required(permission_name="Manage discounts")
def add_discount_to_products(request):
    """
    This function adds the specified discount to the products with the specified IDs.
    The function receives the following parameters:
    - discount_id: the ID of the discount to add
    - product_ids: a list of product IDs to add the discount to
    If the discount is added to all the specified products successfully, the function returns a JSON response with a success message.
    If an error occurs during the discount addition process, the function returns a JSON response with an error message and the error details.
    """
    try:
        session = sessionmaker(bind=engine)() # Start a new database session
        
        product_names = request.POST.getlist('product_names') 
        discount_name = request.POST.get('name')
        
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
        session.commit()
        session.close()
        
        # Return a JSON response with a success message
        response = JsonResponse({'Success':'True', 'message':'The discount has been added to the specified products successfully.'}, status=200)
        add_get_params(response)
        return response
    
    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when adding the discount to the products.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@token_required
@permission_required(permission_name="Manage discounts")
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
    try:
        # Get the parameters from the request object
        discount_id = request.POST.get('discount_id')
        discount_name = request.POST.get('name')
        discount_description = request.POST.get('description')
        discount_percent = request.POST.get('discount_percent')
        active = request.POST.get('active')

        if not discount_id:
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Discount ID must be filled'}, status=404)
            add_get_params(response)
            return response

        session = sessionmaker(bind=engine)()

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

        # Commit the changes to the database and close the session
        session.commit()
        session.close()

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

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when updating the discount.", e, 404)
        add_get_params(response)
        return response


@csrf_exempt
@token_required
@permission_required(permission_name="Manage discounts")
def discount_delete(request):
    """
    This function handles the deletion of a discount from a product.
    The function receives the discount ID from the request object and deletes the discount with that ID.
    If the discount deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the discount deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the discount ID from the request object
        discount_name = request.GET.get('discount_name')

        if not discount_name:
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Discount name must be filled'}, status=404)            
            add_get_params(response)
            return response
        
        session = sessionmaker(bind=engine)() # Start a new database session
        
        # Get the discount with the given ID
        discount = session.query(Discount).filter_by(name=discount_name).first()
        
        if not discount:
            response = JsonResponse({'answer':'False', 'message':'Discount not found'}, status=404)            
            add_get_params(response)
            return response
        
        # Delete the discount from the database and commit the changes
        session.delete(discount)
        session.commit()
        session.close()
        
        # Return a JSON response with a success message
        response = JsonResponse({'Success': 'The discount has been successfully deleted.'}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when deleting the discount.", e, 404)
        add_get_params(response)
        return response



# @permission_required(permission_name="GOD MODE")
# @token_required
@csrf_exempt
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
@token_required
@permission_required(permission_name="Manage product categories")
def delete_null_category_subcategories(request):
    """
    This function deletes all subcategories that have a null category_id.
    """
    session = sessionmaker(bind=engine)()

    # query to get all products that have a null subcategory_id
    null_category_subcategories = session.query(
        Subcategory).filter(Subcategory.category_id == None).all()
    # Iterate through the products and delete them one by one
    for category in null_category_subcategories:
        session.delete(category)
        session.commit()
        print(
            f"Deleted {len(null_category_subcategories)} products with null subcategory_id")
        # Return the number of deleted products for confirmation
    
    response = JsonResponse({"message":"deleted all subcategories that have a null category_id succesfully.", "length_of_null_category_subcategories": len(null_category_subcategories)},status=200)
    add_get_params(response)
    return response



@csrf_exempt
@token_required
@permission_required(permission_name="Manage products")
def delete_null_subcategory_products(request):
    """
    This function deletes all products that have a null subcategory_id.
    """
    session = sessionmaker(bind=engine)()

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

