from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.models import ProductEntry, ProductFag
from DjApp.decorators import permission_required, login_required, require_http_methods

@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
@login_required
def get_self_rates(request):
    
    """
    This function is used to retrieve the next 5 product entries from the database
    starting from the given offset.
    """
    user_rates = request.person.user.product_rates

    user_rates =  [rate.to_json() for rate in user_rates]

    # Convert each entry to a dictionary using list comprehension

    return JsonResponse({'user_rates': user_rates}, status=200)



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
@login_required
def get_self_comments(request):
    
    """
    This function is used to retrieve the next 5 product entries from the database
    starting from the given offset.
    """
    person_comments = request.person.comments

    person_comments_json =  [comment.to_json() for comment in person_comments]

    # Convert each entry to a dictionary using list comprehension

    return JsonResponse({'person_comments': person_comments_json}, status=200)



@csrf_exempt
@require_http_methods(["GET","OPTIONS"])
def get_product_entry_fags(request,product_entry_id):
    
    """
    This function is used to retrieve the next 5 product entries from the database
    starting from the given offset.
    """
    session = request.session
    product_entry = session.query(ProductEntry).get(product_entry_id)
    product_fags = product_entry.get_all_fags()['fags_data']
    
    # Convert each entry to a dictionary using list comprehension

    return JsonResponse({'product_fags': product_fags}, status=200)