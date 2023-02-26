from operator import and_
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from ..models import  Product, ProductComment, Users
from DjAdvanced.settings import engine



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_comment_to_product(request):
    """
    This function handles adding a comment to a product. It receives the following parameters from the request object:
    - user_id: the ID of the user who posted the comment
    - product_id: the ID of the product to which the comment is posted
    - comment: the comment text
    - rate: the rating of the product
    If the comment is added successfully, the function returns a JSON response with a success message and the comment's information.
    If an error occurs during the comment creation process, the function returns a JSON response with an error message and the error details.
    """
    # Parse request data
    data = request.data
    user_id = request.person.user[0].id
    product_id = data.get('product_id')
    session = request.session
    comment_text = data.get('comment')
    rate = data.get('rate')


    product = session.query(Product).get(product_id).one_or_none()
    
    # Check if all required data is present
    if not (user_id and product_id and comment_text and rate and product):
        return JsonResponse({'message': 'Missing data error. User ID, product ID or product, comment text and rate must be filled.'}, status=400)


    # Check if comment already exists, or return 404 error if found
    if session.query(ProductComment).filter_by(user_id=user_id, product_id=product_id).exists():
        return JsonResponse({'message': 'User comment already exists.'}, status=404)

    # Create a new comment object with the given parameters
    new_comment = ProductComment(
        user_id=user_id,
        product_id=product_id,
        ip=request.META.get('REMOTE_ADDR', ''),
        comment=comment_text,
        status='published'
    )
    new_comment.rate = rate

    # Add the new comment to the database and commit the changes
    session.add(new_comment)
    
    
    # Return a JSON response with a success message and the comment's information
    return JsonResponse({'message': 'Comment added successfully.', 'comment_id': new_comment.id, 'user_id': user_id, 'product_id': product_id, 'comment': comment_text, 'rate': rate}, status=200)




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_comment_product(request):
    """
    This function handles updating a comment on a product by ID.
    The function receives the following parameters from the request object:
    - comment_id: the ID of the comment to be updated
    - comment: the updated comment text
    - rate: the updated rating of the comment
    - status: the updated status of the comment (approved, rejected or pending)
    If the comment update is successful, the function returns a JSON response with a success message and the updated comment's information.
    If the specified comment ID does not exist, the function returns a JSON response with an error message and status code 404.
    If an error occurs during the comment update process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        session = request.session
        user_id = request.person.user[0].id
        comment_id = data.get('comment_id')
        comment_text = data.get('comment')
        rate = data.get('rate')
        status = data.get('status')
        
        if not (comment_id and comment_text and rate and status):
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Comment ID, comment text, rate and status must be filled.'}, status=400)
            add_get_params(response)
            return response
        

        # Query the comment by ID
        comment_obj = session.query(ProductComment).get(comment_id)
        if not (comment_obj and (comment_id.user_id == user_id)):
            response = JsonResponse({'answer':'False', 'message':'Comment not found or you do not have permission to this comment.'}, status=404)
            add_get_params(response)
            return response

        # Update the comment object with the new parameters
        comment_obj.comment = comment_text
        comment_obj.rate = rate
        
        
        # Return a JSON response with a success message and the updated comment's information
        response = JsonResponse({'answer': 'True', 'message': 'Comment has been successfully updated.', 'comment_id': comment_obj.id, 'comment': comment_obj.comment, 'rate': comment_obj.rate, 'status': comment_obj.status}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when updating the comment.', e, 500)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_comment_product(request):
    """
    This function handles the deletion of a product comment. The function receives the following parameters from the request object:
    - comment_id: the ID of the comment to delete.
    If the comment deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the comment deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        data = request.data
        user_id = request.person.user[0].id
        comment_id = data.get('comment_id')
        session = request.session
    
        if not (comment_id and user_id):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Comment ID must be provided.'}, status=404)            
            add_get_params(response)
            return response
        
        # Check if the comment exists
        comment_obj = session.query(ProductComment).get(comment_id)
        if not (comment_obj and (comment_obj.user_id == user_id)):
            response = JsonResponse({'answer':'False', 'message':'Comment not found or you do not have permission to this comment.'}, status=404)
            add_get_params(response)
            return response

        # Delete the comment from the database
        session.delete(comment_obj)

        # Return a JSON response with a success message
        response = JsonResponse({"Success":"Comment deleted successfully."}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when deleting the comment.", e, 404)
        add_get_params(response)
        return response
