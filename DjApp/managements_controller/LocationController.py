import uuid
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from ..helpers import GetErrorDetails, add_get_params
from ..models import Country, Location
from ..decorators import permission_required, login_required, require_http_methods
from .TokenController import generate_new_refresh_token, generate_new_access_token
from .MailController import send_email
import re





@csrf_exempt
def create_address_object(session, data):
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
    

    
    state = data.get('state')
    city = data.get('city')
    
    addres_line_1 = data.get('addres_line_1')
    district = data.get('district')
    postal_code = data.get('postal_code')
    description = data.get('description')


    country_name = data.get('country_name')
    
    if not (addres_line_1 and city and country_name and state and postal_code):
        response = JsonResponse(
            {'answer': 'False', 'message': 'Missing data error. Addres line 1, City, State, Postal Code F and Telephone section must be filled'}, status=404)
        add_get_params(response)
        return response

    if(
        country := session.query(Country).filter_by(name = country_name).first()
    ):
        
        country_id = country.id
    else:
        
        country_short_name = data.get('country_short_name')
        country_currency_code = data.get('currency_code')
        country_currency_symbol = data.get('currency_symbol')
        country_phone_code = data.get('country_phone_code')
    
        new_country = Country(
            name = country_name,
            short_name = country_short_name,
            currency_code = country_currency_code,
            currency_symbol = country_currency_symbol,
            phone_code = country_phone_code,
        )
        session.add(new_country)
        session.commit()
        
        country_id = new_country.id 


    # Create a new address object with the given parameters
    new_address = Location(
        country_id = country_id,
        state = state,
        city = city,
        addres_line_1 = addres_line_1,
        postal_code = postal_code,
        district = district,
        description = description,
       
        created_at = datetime.datetime.now(),
        updated_at = datetime.datetime.now(),
    )

    # Add the new address to the database and commit the changes
    session.add(new_address)

    session.commit()
    # Return a JSON response with a success message and the new address's information
    return new_address



@csrf_exempt
def update_object_address(session, obj_address, data ):
    """ 
    This function is used to update an existing user_adres in the database.
    Parameters:
        new_values (Dict[str, Union[str, float]]): A dictionary of the new values for the product. The keys in the dictionary should correspond to the names of the columns in the 'userAddres' table, and the values should be the new values for each column.
    """
    
    
    if country_name := data.get('country_name'):
        if(
            country := session.query(Country).filter_by(name = country_name).first()
        ):
            
            country_id = country.id
        else:
            
            country_short_name = data.get('country_short_name')
            country_currency_code = data.get('currency_code')
            country_currency_symbol = data.get('currency_symbol')
            country_phone_code = data.get('country_phone_code')
        
            new_country = Country(
                name = country_name,
                short_name = country_short_name,
                currency_code = country_currency_code,
                currency_symbol = country_currency_symbol,
                phone_code = country_phone_code,
            )
            session.add(new_country)
            session.commit()
            
            country_id = new_country.id 
        
        obj_address.country_id = country_id        

    if not data:
        response = JsonResponse(
            {'answer': 'new_values are required fields'}, status=400)
        add_get_params(response)
        return response

    # Update the values for each column in the users table
    for column_name, value in data.items():
        print(f"{column_name}:{value}")
        setattr(obj_address, column_name, value)

    return obj_address

