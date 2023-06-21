from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..models import ProductMaterial


@csrf_exempt
@require_http_methods(["POST"])
def add_material(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data
    name = data.get('name')

    material = ProductMaterial.add_material(session, name=name)

    return JsonResponse(
        {"color": material.to_json(), 'answer': "success"}, status=200
    )
