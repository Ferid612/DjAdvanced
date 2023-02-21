from operator import and_
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from .models import  Country, Product, ProductComment, Users
from DjAdvanced.settings import engine


@csrf_exempt
@require_http_methods(["POST"])
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

        if not (country_code and country_name and currency_code):
            response = JsonResponse({'message': 'Missing data error. Country code, country name, and currency code must be filled.'}, status=400)
            return response

        # Create a new country object with the given parameters
        new_country = Country(
            country_code=country_code,
            country_name=country_name,
            currency_code=currency_code,
        )

        # Add the new country to the database and commit the changes
        with session_scope() as session:
            session.add(new_country)

        # Return a JSON response with a success message and the country's information
        response = JsonResponse({'message': 'Country added successfully.', 'country_id': new_country.id, 'country_code': country_code, 'country_name': country_name, 'currency_code': currency_code}, status=200)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when adding the country.', e, 500)
        return response



@csrf_exempt
@require_http_methods(["POST"])
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
    countries = data.get('countries')


    # Lists to keep track of existing and added countries
    existing_countries = []
    added_countries = []

    with session_scope() as session:
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
