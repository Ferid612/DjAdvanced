
import datetime
import uuid
from django.utils.html import escape
from django.http import JsonResponse
import jwt
from sqlalchemy.orm import  sessionmaker
from contextlib import contextmanager
import json, traceback
from DjAdvanced.settings import SECRET_KEY, engine
from DjApp.models import Person




ACCESS_TOKEN_EXPIRATION_TIME = 15
REFRESH_TOKEN_EXPIRATION_TIME = 7



def get_person_from_access_token(request, session, access_token):
    try:
        
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])        
        
    except jwt.exceptions.ExpiredSignatureError:
        return handle_expired_access_token(request, session)
    
    person_id = decoded_token.get('person_id')
    
    
    person = session.query(Person).get(person_id)
    
    access_token = check_access_token(access_token,person_id)
    
    return {
    'refresh_token': request.data.get('refresh_token'),       
    'access_token': access_token,    
    'person':person
    }




def handle_expired_access_token(request, session):
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return JsonResponse({'answer':"False",'message': 'Token has expired and no refresh token is provided'}, status=401)
    
    try:
        decoded_refresh_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        print("test")
        return JsonResponse({'answer':"False",'message': 'Refresh token has expired'}, status=401)

    person_id = decoded_refresh_token.get('person_id')
    person = session.query(Person).get(person_id)

    if not person:
        return JsonResponse({'answer':"False",'message': 'Invalid refresh token'}, status=401)

    if person.refresh_token_id != decoded_refresh_token.get("refresh_token_id"):
        return JsonResponse({'answer':"False",'message': 'Invalid refresh token. err:refresh_token_id '}, status=401)
    
    if decoded_refresh_token['exp'] <= datetime.datetime.utcnow().timestamp():
        return JsonResponse({'answer':"False",'message': 'Refresh token has expired'}, status=401)
    
    
    new_access_token = generate_new_access_token(person_id).get('token')
        
    refresh_token = check_refresh_token(refresh_token, decoded_refresh_token, person, session)    
    
    
    return {
    'refresh_token': refresh_token,       
    'access_token': new_access_token,    
    'person':person
    }




def check_access_token(access_token:str, person_id:object) -> str:
    """Checks if the access token is valid and not expired.
    If the token has expired, a new access token is generated and returned.

    Args:
        access_token (str): Access token to be checked
        person (object): Person object containing the person_id

    Returns:
        str: Valid access token
    """
    
    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
    
    # Generate a new access token if current access token has expired
    access_token_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    if decoded_token['exp'] <= access_token_expiration_time.timestamp():
        access_token = generate_new_access_token(person_id).get('token')
        
    return access_token




def check_refresh_token(refresh_token, decoded_refresh_token, person, session):
    """Checks if the refresh token is valid and not expired.
    If the token has expired, a new refresh token is generated and returned.

    Args:
        refresh_token (str): Refresh token to be checked
        decoded_refresh_token (object): Decoded refresh token payload
        person (object): Person object containing the person_id
        session (object): Database session object

    Returns:
        str: Valid refresh token
    """
    
    # Generate a new refresh token if current refresh token has expired
    refresh_token_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    if decoded_refresh_token['exp'] <= refresh_token_expiration_time.timestamp():
        refresh_token = generate_new_refresh_token(person, session).get('token')
        
    return refresh_token





def generate_new_refresh_token(person, session,days=REFRESH_TOKEN_EXPIRATION_TIME):
    """Generates a new refresh token with a unique refresh_token_id and expiration time of 3 days.

    Args:
        person (object): Person object containing the person_id
        session (object): Database session object

    Returns:
        dict: Dictionary containing the refresh_token_id, token, and expiration time
    """
    
    refresh_token_id = str(uuid.uuid4())
    
    days = datetime.timedelta(days=days)
    expiration_time = datetime.datetime.utcnow() + days
    
    refresh_token_payload = {
        'refresh_token_id': refresh_token_id,
        'person_id': person.id,
        'exp': expiration_time,
    }
    refresh_token  = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm="HS256")
    
    person.refresh_token_id = refresh_token_id

    session.add(person)
    session.commit()
        
    return {
        'refresh_token_id': refresh_token_id,
        'token': refresh_token,
        'exp': expiration_time
    }
    
    



def generate_new_access_token(person_id, minutes=ACCESS_TOKEN_EXPIRATION_TIME):
    
    """Generates a new access token with an expiration time of 5 minutes.

    Args:
        person (object): Person object containing the person_id

    Returns:
        dict: Dictionary containing the token and expiration time
    """
    minutes = datetime.timedelta(minutes=minutes)
    expiration_time = datetime.datetime.utcnow() + minutes
    
    access_token_payload = {
        'person_id': person_id,
        'exp': expiration_time,
    }
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm="HS256")
    
    return {
        'token': access_token,
        'exp': expiration_time
    }

