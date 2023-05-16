from DjApp.helpers import add_get_params
from DjApp.models import Campaign
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def get_campaign(request, campaign_id):
    """
    Get a campaign with the given ID.

    Args:
        request (HttpRequest): An HTTP request object.
        campaign_id (int): The ID of the campaign to retrieve.

    Returns:
        JsonResponse: A JSON response containing the status of the operation and the retrieved campaign data.
    """

    # Get the SQLAlchemy session from the request object
    session = request.session

    # Retrieve the campaign from the database based on the campaign_id
    campaign = session.query(Campaign).get(campaign_id)

    # Check if the campaign exists
    if not campaign:
        response = JsonResponse(
            {'answer': 'False', 'message': 'Campaign not found'},
            status=404)
        add_get_params(response)
        return response

    # Retrieve all product entries associated with the campaign
    product_entries = campaign.product_entries

    # Convert the campaign and product entries to JSON-compatible dictionaries
    campaign_data = campaign.to_json()
    product_entries_data = [product_entry.to_json() for product_entry in product_entries]

    # Add the product entries data to the campaign data
    campaign_data['product_entries'] = product_entries_data

    # Return a JSON response containing the retrieved campaign data with product entries
    response = JsonResponse({
        "answer": "Campaign retrieved successfully.",
        "campaign": campaign_data
    }, status=200)

    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["GET"])
def get_all_campaigns(request):
    """
    Get all campaigns.

    Args:
        request (HttpRequest): An HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the status of the operation and the retrieved campaigns data.
    """

    # Get the SQLAlchemy session from the request object
    session = request.session

    # Retrieve all campaigns from the database
    campaigns = session.query(Campaign).all()

    # Convert the campaigns to a list of JSON objects
    campaigns_data = [campaign.to_json() for campaign in campaigns]

    # Return a JSON response containing the retrieved campaigns data
    response = JsonResponse({
        "answer": "Campaigns retrieved successfully.",
        "campaigns": campaigns_data
    }, status=200)

    add_get_params(response)
    return response