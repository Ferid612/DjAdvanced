from DjApp.models import Campaign, CampaignProduct, ProductEntry
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from datetime import datetime


@csrf_exempt
@require_http_methods(["POST"])
def create_campaign(request):
    """
    Create a campaign request with the given data.

    Args:
        request (HttpRequest): An HTTP request object containing the campaign data in the request body.

        session (Session): The SQLAlchemy session object.
        name (str): The name of the campaign.
        description (str): The description of the campaign.
        valid_from (datetime): The starting date and time of the campaign.
        valid_to (datetime): The ending date and time of the campaign.

    Returns:
        JsonResponse: A JSON response containing the status of the operation and any relevant data.
        
        
    Example campaign data:
        campaign_data = {
            "name": "Buy 2 Get 1 Free",
            "description": "Buy 2 products and get 1 product for free.",
            "valid_from": datetime.now(),
            "valid_to": datetime(2023, 12, 31)
        }

    """

    # Get the campaign data from the request body
    data = request.data
    name = data.get('name')
    description = data.get('description')
    valid_from = datetime.fromisoformat(data.get('valid_from'))
    valid_to = datetime.fromisoformat(data.get('valid_to'))

    # Check if any required data is missing
    if not (name and description and valid_from and valid_to):
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. Name, Description, Valid From and Valid To must be filled',
            },
            status=404,
        )
    # Get the SQLAlchemy session from the request object
    session = request.session

    # Check if a campaign with the given name already exists
    if session.query(Campaign).filter_by(name=name).one_or_none():
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Campaign with that name already exists',
            },
            status=404,
        )
    # Create the campaign object
    campaign = Campaign(name=name, description=description,
                        valid_from=valid_from, valid_to=valid_to)

    # Add the campaign to the session and commit the changes
    session.add(campaign)
    session.commit()

    return JsonResponse(
        {
            "answer": "Created campaign object successfully.",
            "campaign": campaign.to_json(),
        },
        status=200,
    )





@csrf_exempt
@require_http_methods(["POST"])
def assign_campaign_to_products(request):
    """
    Assign products to a campaign with the given data.

    Args:
        request (HttpRequest): An HTTP request object containing the campaign and product data in the request body.

    Returns:
        JsonResponse: A JSON response containing the status of the operation and any relevant data.
    
    Example campaign data:
        campaign_id : 1,
        "campaign_products": [
            {
                "product_id": 1,
                "quantity_required": 2,
                "quantity_discounted": 1
            }
        ]
    
    """

    # Get the campaign and product data from the request body
    data = request.data
    campaign_id = data.get('campaign_id')
    campaign_products = data.get('campaign_products')

    # Check if any required data is missing
    if not (campaign_id and campaign_products):
        return JsonResponse(
            {
                'answer': 'False',
                'message': 'Missing data error. Campaign ID and Campaign Products must be provided',
            },
            status=404,
        )
    # Get the SQLAlchemy session from the request object
    session = request.session

    # Retrieve the campaign from the database based on the campaign_id
    campaign = session.query(Campaign).get(campaign_id)

    # Check if the campaign exists
    if not campaign:
        return JsonResponse(
            {'answer': 'False', 'message': 'Campaign not found'}, status=404
        )
    # Assign the products to the campaign
    for product_data in campaign_products:
        product_id = product_data.get('product_id')
        quantity_required = product_data.get('quantity_required')
        quantity_discounted = product_data.get('quantity_discounted')

        # Retrieve the product entry from the database based on the product_id
        product_entry = session.query(ProductEntry).get(product_id)

        # Check if the product entry exists
        if not product_entry:
            return JsonResponse(
                {
                    'answer': 'False',
                    'message': f"Product entry not found for product ID {product_id}",
                },
                status=404,
            )
        # Create the campaign product and associate it with the campaign and product_entry
        campaign_product = CampaignProduct(
            campaign=campaign,
            product_entry=product_entry,
            quantity_required=quantity_required,
            quantity_discounted=quantity_discounted
        )

        # Add the campaign product to the campaign's product_entries collection
        campaign.product_entries.append(campaign_product)

    # Commit the changes to the session
    session.commit()

    return JsonResponse(
        {"answer": "Products assigned to the campaign successfully."},
        status=200,
    )


