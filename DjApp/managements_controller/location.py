import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from ..helpers import GetErrorDetails, add_get_params, session_scope
from ..models import Country, Location
from ..decorators import permission_required, login_required, require_http_methods
from .tokens import  generate_new_refresh_token,generate_new_access_token 
from .mail_sender import send_email
import re




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_country(request):
    """
    Add a new country to the database.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        country_code = data.get('country_code')
        country_name = data.get('country_name')
        currency_code = data.get('currency_code')
        session = request.session

        if not (country_code and country_name and currency_code):
            response = JsonResponse({'message': 'Missing data error. Country code, country name, and currency code must be filled.'}, status=400)
            add_get_params(response)
            return response

        # Create a new country object with the given parameters
        new_country = Country(
            country_code=country_code,
            country_name=country_name,
            currency_code=currency_code,
        )

        # Add the new country to the database and commit the changes

        session.add(new_country)

        # Return a JSON response with a success message and the country's information
        response = JsonResponse({'message': 'Country added successfully.', 'country_id': new_country.id, 'country_code': country_code, 'country_name': country_name, 'currency_code': currency_code}, status=200)
        add_get_params(response)
      
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when adding the country.', e, 500)
        add_get_params(response)
      
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_countries(request):
    """
    This function handles adding multiple countries to the database. It receives a list of countries in the following format:
    [
        {
            "country_code": "1",
            "country_name": "Country 1",
            "currency_code": "CUR1"
        },
        {
            "country_code": "2",
            "country_name": "Country 2",
            "currency_code": "CUR2"
        },
        ...
    ]
    If the countries are added successfully, the function returns a JSON response with a success message and the countries' information.
    If an error occurs during the country creation process, the function returns a JSON response with an error message and the error details.
    """
    
    # Get the list of countries from the request
    data = request.data
    session = request.session
    
    countries = data.get('countries')


    # Lists to keep track of existing and added countries
    existing_countries = []
    added_countries = []

    
    # Create a session for database operations
    existing_countries = [c.country_name for c in session.query(Country.country_name).filter(Country.country_name.in_([country.get('country_name') for country in countries])).all()]
    added_countries = [country for country in countries if country.get('country_name') not in existing_countries]

    # Create new country objects for the added countries
    new_countries = []
    for country in added_countries:
        new_country = Country(
            country_code=country.get('country_code'),
            country_name=country.get('country_name'),
            currency_code=country.get('currency_code')
        )
        new_countries.append(new_country)

    # Insert the new countries into the database
    session.bulk_save_objects(new_countries)

    # Return a JSON response with the existing and added countries
    response_data = {'existing_countries': existing_countries, 'added_countries': [c.country_name for c in new_countries]}
    response = JsonResponse(response_data, status=200)
    add_get_params(response)
    return response





@csrf_exempt
def add_address_to_object(request,adding_object):
    """
    This function handles person address creation by creating a new address and adding it to the user's account.
    The function receives the following parameters from the request object:
    - person_id: the ID of the person to add the address to
    - addres_line_1: the first line of the user's address
    - addres_line_2: the second line of the user's address (optional)
    - city: the city of the user's address
    - postal_code: the postal code of the user's address
    - country: the country of the user's address
    - telephone: the telephone number of the user
    If the address creation is successful, the function returns a JSON response with a success message and the new address's information.
    If an error occurs during the address creation process, the function returns a JSON response with an error message and the error details.
    """

    # Get the parameters from the request object
    data = request.data
    
    session = request.session
    
    

    addres_line_1 = data.get('addres_line_1')
    addres_line_2 = data.get('addres_line_2')
    city = data.get('city')
    postal_code = data.get('postal_code')
    state = data.get('state')
    district = data.get('district')
    location_type_code = data.get('state')
    country_name = data.get('country')
    description = data.get('description')

    if not (addres_line_1 and city and country_name and state and postal_code):
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. Addres line 1, City, State, Postal Code Country and Telephone section must be filled'}, status=404)
        add_get_params(response)
        return response



    country_id =session.query(Country).filter_by(country_name = country_name).fisrt().id
    if not country_id:
        response = JsonResponse(
            {'answer': 'False', 'message': "Country name don't findi."}, status=404)
        add_get_params(response)
        return response

    # Create a new address object with the given parameters
    new_address = Location(
        country_id=country_id,
        city=city,
        addres_line_1=addres_line_1,
        addres_line_2=addres_line_2,
        postal_code=postal_code,
        # location_type_code = location_type_code ,
        district = district,
        description = description,
        creadet_at=datetime.datetime.now(),
        modified_at=datetime.datetime.now(),
    )

    adding_object.location = new_address
    # Add the new address to the database and commit the changes
    session.add(new_address)


    # Return a JSON response with a success message and the new address's information
    response = JsonResponse({"Success": "The new address has been successfully added to the user's account.", "addres_line_1": addres_line_1,
                            "addres_line_2": addres_line_2, "city": city, "postal_code": postal_code, "country_id": country_id}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
def update_object_address(request,updated_object):
    """
    This function is used to update an existing user_adres in the database.
    Parameters:
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'userAddres' table, and the values should be the new values for each column.
    """
    
    data = request.data
    session = request.session
    

    new_values = data.get('new_values')
    if not new_values:
        response = JsonResponse(
            {'answer': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response


    location = session.query(Location).filter_by(id=updated_object.location_id).first()
    # Update the values for each column in the users table
    for index, new_value in enumerate(new_values):
        for column_name, value in new_value.items():
            print(f"{column_name}:{value}")
            setattr(location, column_name, value)

   
    response = JsonResponse(
        {'Success': 'The object address has been successfully updated'}, status=200)
    add_get_params(response)
    return response
