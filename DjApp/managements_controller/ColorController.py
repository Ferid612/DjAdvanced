from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import add_get_params
from ..models import  ProductColor


@csrf_exempt
@require_http_methods(["POST"])
def add_color(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data
    name = data.get('name')
    color_code = data.get('color_code')
    if not name or not color_code:
        response = JsonResponse({'message': 'Please provide a name and a color code'}, status=400)
        add_get_params(response)
        return response
    
    color = ProductColor.add_color(session, name=name, color_code=color_code)
    
    
    response = JsonResponse({"color":color.to_json(),'answer': "success"}, status=200)
    add_get_params(response)
    return response