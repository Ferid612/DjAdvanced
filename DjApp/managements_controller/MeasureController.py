from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..models import ProductMeasure


@csrf_exempt
@require_http_methods(["POST"])
def add_measure(request):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    measure_name = request.data.get('measure_name')
    session = request.session
    new_measure = ProductMeasure.add_measure(session, measure_name)

    print(new_measure.name)

    return JsonResponse({'answer': "success"}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def add_measure_values(request, measure_id):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    session = request.session
    data = request.data

    values = data.get('values')
    product_measure = session.query(ProductMeasure).get(measure_id)

    for value in values:
        product_measure.append_value(session, value)

    return JsonResponse({'answer': "success"}, status=200)
