from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import require_http_methods
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

    measure = session.query(ProductMeasure).filter_by(
        name=measure_name).one_or_none()
    if measure is not None:
        return JsonResponse({
            'answer': 'unsuccessful',
            'message': 'Measure is already exist.',
            'measure': measure.to_json()
        }, status=200)

    measure = ProductMeasure.add_measure(session, measure_name)

    print(measure.name)

    return JsonResponse({
        'answer': 'successful',
        'message': 'New measure successfully added.',
        'measure': measure.to_json()

    }, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def add_measure_values(request, measure_id):
    """
    Adds new child values to an existing product measure in the database.
    If the product measure does not exist, the values will not be added.
    """

    try:
        session = request.session
        data = request.data

        values = data.get('values')
        product_measure = session.query(ProductMeasure).get(measure_id)

        if product_measure is None:
            return JsonResponse({'answer': 'Product measure not found.', 'data': None}, status=404)

        exist_measure_values = [product_measure.value for product_measure in product_measure.values]

        new_values = [value for value in values if value not in exist_measure_values]
        for value in new_values:
            product_measure.append_value(session, value)

        return JsonResponse({'answer': 'success',
                             'message': 'New values successfully added to the product measure.',
                             'product_measure': product_measure.to_json()}, status=200)

    except Exception as e:
        return JsonResponse({'answer': 'An error occurred.',
                             'message': str(e)}, status=500)
