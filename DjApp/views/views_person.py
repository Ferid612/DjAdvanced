from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails
from DjAdvanced.settings.production import engine
from DjApp.models import Person, ProfilImage
# from ..models import Users


@csrf_exempt
@require_http_methods(["POST", "GET", "OPTIONS"])
@login_required
def get_person(request):
    """
    API endpoint to retrieve user information by username.
    The user data includes the following fields:
    - id
    - username
    - usermail
    - first_name
    - last_name
    - telephone
    - created_at
    - update_at   
    - active
    - phone_verify
    """
    try:
        # Get the user object associated with the request
        person = request.person
        # Build the user data dictionary
        user_data = person.to_json()

        return JsonResponse(user_data, status=200)
    except Exception as e:
        return GetErrorDetails(
            "An error occurred while getting user information.", e, 500
        )


@csrf_exempt
@require_http_methods(["POST", "GET", "OPTIONS"])
@login_required
def get_person_data_by_username(request):
    """
    API endpoint to retrieve user information by username.
    The user data includes the following fields:
    - id
    - username
    - usermail
    - first_name
    - last_name
    - telephone
    - created_at
    - update_at
    - active
    - phone_verify
    """
    try:
        # Get the user object associated with the request
        person = request.person

        # Build the user data dictionary
        user_data = person.to_json()

        return JsonResponse(user_data, status=200)
    except Exception as e:
        return GetErrorDetails(
            "An error occurred while getting user information.", e, 500
        )


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def get_all_persons_data(request):
    """
    API endpoint to retrieve all person data in JSON format.
    """
    # Get all persons from the database
    session = request.session

    persons = session.query(Person).all()

    # Build a list of person data dictionaries
    persons_data = []
    for person in persons:
        person_data = person.to_json()
        persons_data.append(person_data)

    # Return a JSON response with the person data
    response_data = {
        "persons": persons_data
    }
    return JsonResponse(response_data, status=200)


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def get_person_profil_image(request, image_id):
    session = request.session

    if profil_image := session.query(ProfilImage).get(image_id):
        return JsonResponse(
            {"profil_image": profil_image.to_json()}, status=200
        )
    else:
        return JsonResponse(
            {'answer': "Profil image don't exist."}, status=501
        )


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@login_required
def get_person_address(request):
    
    if person_location := request.person.location:
        return JsonResponse(
            {"person_location": person_location.to_json()}, status=200
        )
    else:
        return JsonResponse(
            {'answer': "Person location don't exist."}, status=501
        )
