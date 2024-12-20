from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DeltaConfApp.models import CardBox, ImageGallery, NewArrival, SlidePhotos
from DjApp.decorators import require_http_methods
from DjApp.helpers import GetErrorDetails
    
    

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_slide_photos(request):
    """
    Get all slide photos in the SlidePhotos table

    Parameters:
        None

    Returns:
        A JSON response containing a list of dictionaries, where each dictionary represents a slide photo.
    """
    session = request.session

    slide_photos = session.query(SlidePhotos).all()
    slide_photo_dicts = [photo.to_json() for photo in slide_photos]

    response_data = {"slide_photos": slide_photo_dicts}
    return JsonResponse(response_data, status=200)



@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_new_arrivals(request):
    """
    Get all new arrival in the NewArrival table

    Parameters:
        None

    Returns:
        A JSON response containing a list of dictionaries, where each dictionary represents a new arrivals.
    """
    session = request.session

    new_arrivals = session.query(NewArrival).all()
    new_arrivals_dict = [new_arrival.to_json() for new_arrival in new_arrivals]

    response_data = {"new_arrivals": new_arrivals_dict}
    return JsonResponse(response_data, status=200)



@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_galleries(request):
    """
    Get all slide photos in the SlidePhotos table

    Parameters:
        None

    Returns:
        A JSON response containing a list of dictionaries, where each dictionary represents a slide photo.
    """
    session = request.session

    galleries = session.query(ImageGallery).all()
    gallery_dicts = [gallery.to_json() for gallery in galleries]

    response_data = {"gallery_dicts": gallery_dicts}
    return JsonResponse(response_data, status=200)
    
    
    
    
    
@csrf_exempt
@require_http_methods(["POST","GET","OPTIONS"])
def get_card_box_entries(request,pk):
    try:
        session = request.session
        # Get the user object associated with the request
        card_box = session.query(CardBox).get(pk)

        card_box_with_entries = card_box.to_json_with_entries()
        return JsonResponse(card_box_with_entries, status=200)
    except Exception as e:
        return GetErrorDetails(
            "An error occurred while getting user information.", e, 500
        )
    