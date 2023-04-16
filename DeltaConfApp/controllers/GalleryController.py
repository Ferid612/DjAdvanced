from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import  add_get_params
from ..models import ImageGallery, SlidePhotos



@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
@login_required
# @permission_required("manage_gallery")
def add_slide_photo(request):
    """
    Add a new SlidePhotos object to an existing ImageGallery object

    Parameters:
        image_gallery_id (int): The ID of the ImageGallery object to add the SlidePhotos to
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
    relevant_url = data.get("relevant_url")
    
    
    session = request.session
    
    # Retrieve the ImageGallery object based on the given ID
    gallery = session.query(ImageGallery).filter_by(id=image_gallery_id).one_or_none()

    if not gallery:
        response = JsonResponse({'answer':'False', 'message':'The Image Gallery name  is not exists.'}, status=404)            
        add_get_params(response)
        return response

    # Create a new SlidePhotos object and add it to the ImageGallery's list of slide photos
    slide_photo = SlidePhotos(gallery_id=image_gallery_id,url=url, title=title, relavant_url=relevant_url)
    session.add(slide_photo)
    
    # Commit the changes to the database
    session.commit()
    response = JsonResponse({"Success":"The new slide_photo has been successfully added to gallery."}, status=200)
    add_get_params(response)
    return response


 
@csrf_exempt
@require_http_methods(["POST","OPTIONS"])
@login_required
def add_slide_photos(request):
    """
    Add new SlidePhotos objects to an existing ImageGallery object

    Parameters:
        image_gallery_id (int): The ID of the ImageGallery object to add the slide photos to
        slide_photos (list): A list of dictionaries containing information about each slide photo. Each dictionary should have the following keys:
            - url (str): The URL of the slide photo
            - title (str): The title of the slide photo
            - relevant_url (str): A relevant URL associated with the slide photo

    Returns:
        None
    """
    data = request.data
    image_gallery_id = data.get("image_gallery_id")
    slide_photos = data.get("slide_photos")

    session = request.session
    
    # Retrieve the ImageGallery object based on the given ID
    gallery = session.query(ImageGallery).filter_by(id=image_gallery_id).one_or_none()

    if not gallery:
        response = JsonResponse({'Error': 'The Image Gallery does not exist.'}, status=404)
        add_get_params(response)
        return response
    
    for photo in slide_photos:
        url = photo.get("url")
        title = photo.get("title")
        relevant_url = photo.get("relevant_url")

        # Create a new SlidePhotos object and add it to the ImageGallery's list of slide photos
        slide_photo = SlidePhotos(gallery_id=image_gallery_id,url=url, title=title, relavant_url=relevant_url)
        
        session.add(slide_photo)
    
    # Commit the changes to the database
    session.commit()
    response = JsonResponse({"Success": "The new slide photos have been successfully added to the gallery."}, status=200)
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
@login_required
def create_image_gallery(request):
    """
    Create a new ImageGallery object

    Parameters:
        name (str): The name of the new image gallery
        description (str): A description for the new image gallery

    Returns:
        None
    """
    data = request.data
    name = data.get("name")
    description = data.get("description")

    session = request.session
    
    # Retrieve the ImageGallery object based on the given ID
    gallery = session.query(ImageGallery).filter_by(name=name).one_or_none()

    if gallery:
        response = JsonResponse({'answer':'False', 'message':'The Image Gallery name is allready exists.'}, status=404)            
        add_get_params(response)
        return response
    
    
    # Create a new ImageGallery object with the given name and description
    gallery = ImageGallery(name=name, description=description)

    # Save the new ImageGallery object to the database
    session.add(gallery)
    session.commit()
    response = JsonResponse({"Success": "The new Image Gallery has been successfully created."}, status=200)
    add_get_params(response)
    return response


