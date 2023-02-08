from django.http import JsonResponse
from sqlalchemy import DECIMAL, Boolean, DateTime, Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import  sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjApp.helpers import GetErrorDetails, add_get_params
from .models import Base, Category, Subcategory, Product
from DjAdvanced.settings import engine



@csrf_exempt
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
        

def add_category(request):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    Session = sessionmaker(bind=engine)  # create a new session
    session = Session()  # start a new session
    
    categories = request.POST.getlist('categories')

    added_categories = []
    existing_categories = []
    for category in categories:
        existing_category = session.query(
            Category).filter_by(name=category).one_or_none()
        existing_subcategory = session.query(
            Subcategory).filter_by(name=category).one_or_none()

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
    parent_name = request.POST.get('parent_name')
    new_subcategories = request.POST.getlist('new_subcategories')

    # Create a session for database operations
    Session = sessionmaker(bind=engine)
    session = Session()

    # Lists to keep track of existing and added subcategories
    existing_categories = []
    added_categories = []
    for subcategory in new_subcategories:
        # Check if subcategory or category with the same name already exists
        existing_category = session.query(Category).filter_by(name=subcategory).one_or_none()
        existing_subcategory = session.query(Subcategory).filter_by(name=subcategory).one_or_none()

        if existing_subcategory or existing_category:
            # If subcategory already exists, add it to the existing list and continue
            existing_categories.append(subcategory)
            print(f"{subcategory} already exists")
            
        else:
            # Check if the parent category or subcategory exists
            existing_parent = session.query(Category).filter_by(name=parent_name).one_or_none()
            existing_parent = existing_parent or session.query(Subcategory).filter_by(name=parent_name).one_or_none()

            if existing_parent:
                # If parent exists, add new subcategory and add to added list
                added_categories.append(subcategory)
                new_subcategory = Subcategory(name=subcategory, parent=existing_parent)
                session.add(new_subcategory)
                
    # Commit the changes to the database
    session.commit()
    # Return a json response with the existing and added subcategories
    response =  JsonResponse({'existing_categories': existing_categories,'added_categories':added_categories}, status=200)
    add_get_params(response)
    return response


def add_products_to_subcategory(request):
    """
    This function is used to add products to a specific subcategory. 
    It checks if a product with the same name already exists in the database and if so, it does not add it.
     Parameters:
        subcategory_name (str): The name of the subcategory to add the products to.
        product_list (List[Dict[str, Union[str, float, int]]]): A list of dictionaries representing the products to be added. Each dictionary should have keys 'name', 'price', and 'description'.   
    """
    subcategory_name = request.POST.get('subcategory_name')
    product_list = request.POST.getlist('product_list')
    if not subcategory_name or not product_list:
        response =  JsonResponse({'error': 'subcategory_name and product_list are required fields'}, status=400)
        add_get_params(response)
        return response
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    subcategory = session.query(Subcategory).filter(
        (Subcategory.name == subcategory_name)).first()

    # Iterate through the list of products

    existing_products = []
    added_products = []
    # Iterate through the list of products
    for product in product_list:
        # Check if a product with the same name already exists
        existing_product = session.query(Product).filter_by(
            name=product['name']).one_or_none()

        if existing_product:
            existing_products.append(existing_product.name)
        else:
            new_product = Product(name=product['name'], price=product['price'],
                                description=product['description'], subcategory=subcategory)
            session.add(new_product)
            added_products.append(product['name'])

    # Commit the changes to the database
    session.commit()
    response =  JsonResponse({'existing_products': existing_products,'added_products':added_products}, status=200)
    add_get_params(response)
    return response
        

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
    
    Session = sessionmaker(bind=engine)
    session = Session()

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


def delete_product(request):
    """
    This function is used to delete a specific product.
    Parameters:
        product_id (int): The ID of the product to be deleted.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
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

def delete_all_tables(request):
    """ 
    This function deletes all tables.
    """
    user=""
    if user == "Farid":    
        Base.metadata.drop_all(bind=engine)
        response = JsonResponse({"message":"Deleted all tables succesfully."},status=200)
        add_get_params(response)
        return response
    else:
        response = JsonResponse({"message":"User is not admin."},status=200)
        add_get_params(response)
        return response

def delete_null_category_subcategories(request):
    """
    This function deletes all subcategories that have a null category_id.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
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
     
def delete_null_subcategory_products(request):
    """
    This function deletes all products that have a null subcategory_id.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
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

