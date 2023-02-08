from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from sqlalchemy.orm import relationship, sessionmaker
from DjAdvanced.settings import engine
from DjApp.managment_sms_sender import send_verification_code_with_twilio
from .models import Category, Subcategory, Product
from .helpers import add_get_params
import traceback, logging


def hello(request):
    return HttpResponse("Hello world")



@csrf_exempt
def testing(request):
    # Build the POST parameters
    if request.method == 'POST':
        try:
            
            user_region = request.POST.get('user_region')
            response = JsonResponse({'Answer': "Success", })
            # response.status_code=501
            add_get_params(response)
            return response
        except Exception as e:
            my_traceback = traceback.format_exc()

            logging.error(my_traceback)
            response = JsonResponse({
                                    'error_text': str(e),
                                    'error_text_2': my_traceback
                                    })
            response.status_code = 505

            add_get_params(response)
            return response
    else:
        response = JsonResponse(
            {'Answer': "This promerty only for POST method.", })
        response.status_code = 501
        add_get_params(response)
        return response


def get_all_products_by_subcategory_name(request):
    """
    This function returns all products that belong to a subcategory by given subcategory name.
    The subcategory name is passed as a query parameter in the GET request.
    If the subcategory does not exist, it returns a JSON response with an 'Is empty' message.
    If the subcategory_name parameter is not provided in the GET request, it returns a JSON response with an 'error' message.
    """
    # Get the subcategory name from the GET request
    subcategory_name = request.GET.get('subcategory_name')
    
    # Check if the subcategory_name parameter was provided in the GET request
    if not subcategory_name:
        response = JsonResponse({'error': 'subcategory_name is a required parameter'}, status=400)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)  # create a new session
    session = Session()  # start a new session


    # Try to find the subcategory by name in both the Category and Subcategory tables
    existing_category = (session.query(Category)
                        .filter_by(name=subcategory_name)
                        .one_or_none() or
                        session.query(Subcategory)
                        .filter_by(name=subcategory_name)
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

def get_products_by_category_name(request):
    """
    This function retrieves all products belonging to the subcategories under the specified category.
    :param request: HTTP request containing a query parameter 'category_name'
    :return: JsonResponse containing a list of products data in the 'data' key, or an error message if category does not exist
    """
    
    category_name = request.GET.get('category_name')
    if not category_name:
        response = JsonResponse({'error': 'category_name is a required parameter'}, status=400)
        add_get_params(response)
        return response
    Session = sessionmaker(bind=engine)  # create a new session
    session = Session()  # start a new session


    # Get the category object
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
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
    else:
        response = JsonResponse({'error': f"{category_name} does not exist in the category table."}, status=404)
        add_get_params(response)
        return response


def get_categories_and_subcategories(request):
    """
    This function retrieves all categories and their subcategories.
    
    :return: list of dictionaries, each representing a category and its subcategories
    """
    Session = sessionmaker(bind=engine)  # create a new session
    session = Session()  # start a new session

    categories = session.query(Category).all()
    categories_data = []
    for category in categories:
        subcategories = session.query(Subcategory).filter(Subcategory.category_id == category.id).all()
        subcategories_data = [{'name': subcategory.name} for subcategory in subcategories]
        categories_data.append({'category': category.name, 'subcategories': subcategories_data})
    response = JsonResponse({'data': categories_data}, status=200)
    add_get_params(response)
    return response