from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from ..models import ImageGallery, NewArrival


# @login_required
# @permission_required("manage_gallery")
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def add_new_arrival(request):
    """
    Add a new NewArrival object to an existing ImageGallery object

    Parameters:
        image_gallery_id (int): The ID of the ImageGallery object to add the NewArrival to
        url (int): The URL of the slide photo
        title (str): The title of the slide photo
        relevant_url (str): A relevant URL associated with the slide photo

    Returns:
        None
    """
    data = request.data
    image_gallery_id = data.get("image_gallery_id")
    url = data.get("url")
    title = data.get("title")
    index = data.get("index")
    relevant_url = data.get("relevant_url")
    description = data.get("description")

    session = request.session

    if not url or not description or not image_gallery_id or not relevant_url or not index:
        return JsonResponse(
            {'answer': 'unsuccessful', 'message': 'The required data is missing.'},
            status=404,
        )
    # Retrieve the ImageGallery object based on the given ID
    gallery = session.query(ImageGallery).get(image_gallery_id)

    if not gallery:
        return JsonResponse(
            {
                'answer': 'unsuccessful',
                'message': 'The Image Gallery name  is not exists.',
            },
            status=404,
        )
    # Create a new NewArrival object and add it to the ImageGallery's list of slide photos
    new_arrival = NewArrival(gallery_id=image_gallery_id, index=index, url=url,
                             title=title, description=description, relavant_url=relevant_url)
    session.add(new_arrival)

    # Commit the changes to the database
    session.commit()
    return JsonResponse(
        {   
            'answer':'successful',
            'message': 'The new new_arrival has been successfully added to gallery.',
            'new_arrival': new_arrival.to_json(),
        },
        status=200,
    )


# @login_required
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def add_new_arrivals(request):
    """
    Add new NewArrival objects to an existing ImageGallery object

    Parameters:
        image_gallery_id (int): The ID of the ImageGallery object to add the slide photos to
        new_arrival (list): A list of dictionaries containing information about each slide photo. Each dictionary should have the following keys:
            - url (str): The URL of the slide photo
            - title (str): The title of the slide photo
            - relevant_url (str): A relevant URL associated with the slide photo

    Returns:
        None
    """
    data = request.data
    image_gallery_id = data.get("image_gallery_id")
    new_arrival = data.get("new_arrival")

    session = request.session

    # Retrieve the ImageGallery object based on the given ID
    gallery = session.query(ImageGallery).get(image_gallery_id)

    if not gallery:
        return JsonResponse(
            {'Error': 'The Image Gallery does not exist.'}, status=404
        )
    for photo in new_arrival:
        url = photo.get("url")
        title = photo.get("title")
        relevant_url = photo.get("relevant_url")
        index = photo.get("index")
        description = photo.get("description")
        if not index:
            # Create a new NewArrival object and add it to the ImageGallery's list of arrival photos
            arrival_photo = NewArrival(gallery_id=image_gallery_id, url=url,
                                       description=description, title=title, relavant_url=relevant_url)
        else:
            arrival_photo = NewArrival(gallery_id=image_gallery_id, index=index,
                                       description=description, url=url, title=title, relavant_url=relevant_url)

        session.add(arrival_photo)

    # Commit the changes to the database
    session.commit()
    return JsonResponse(
        {
            "Success": "The new arrival photos have been successfully added to the gallery."
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def update_new_arrival(request, new_arrival_id):
    """
    Update an existing NewArrival object

    Parameters:
        new_arrival_id (int): The ID of the NewArrival object to update
        url (int): The URL of the slide photo
        title (str): The title of the slide photo
        relevant_url (str): A relevant URL associated with the slide photo

    Returns:
        None
    """
    data = request.data
    url = data.get("url")
    title = data.get("title")
    index = data.get("index")
    relevant_url = data.get("relevant_url")
    description = data.get("description")

    session = request.session

    # Retrieve the NewArrival object based on the given ID
    new_arrival = session.query(NewArrival).get(new_arrival_id)

    if not new_arrival:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'The New Arrival object is not exists.',
            },
            status=404,
        )
    # Update the NewArrival object's properties
    if url:
        new_arrival.url = url
    if title:
        new_arrival.title = title
    if index:
        new_arrival.index = index
    if relevant_url:
        new_arrival.relavant_url = relevant_url
    if description:
        new_arrival.description = description
    # Commit the changes to the database
    session.commit()
    return JsonResponse(
        {
            "Success": "The new_arrival object has been successfully updated.",
            "new_arrival": new_arrival.to_json(),
        },
        status=200,
    )


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def delete_new_arrival(request, new_arrival_id):
    """
    Delete an existing NewArrival object from the database

    Parameters:
        new_arrival_id (int): The ID of the NewArrival object to delete

    Returns:
        None
    """
    session = request.session

    # Retrieve the NewArrival object based on the given ID
    new_arrival = session.query(NewArrival).get(new_arrival_id)

    if not new_arrival:
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'The New Arrival slide is not exists.',
            },
            status=404,
        )
    # Remove the NewArrival object from the database
    session.delete(new_arrival)
    session.commit()

    return JsonResponse(
        {
            "Success": "The new_arrival slide has been successfully deleted.",
            "new_arrival": new_arrival.to_json(),
        },
        status=200,
    )
