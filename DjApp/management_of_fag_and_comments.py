from operator import and_
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params, session_scope
from .models import  Product, ProductComment, Users
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
    try:
        # Get the parameters from the request object
        data = request.data
        
        user_id = request.user.id
        product_id = data.get('product_id')
        comment_text = data.get('comment')
        rate = data.get('rate')

        if not (user_id and product_id and comment_text and rate):
            response = JsonResponse({'message': 'Missing data error. User ID, product ID, comment text and rate must be filled.'}, status=400)
            return response

        with session_scope() as session:
            
            # Check if the user and product exist
            user = session.query(Users).get(user_id)
            product = session.query(Product).get(product_id)
            if not (user and product):
                response = JsonResponse({'message': 'User or product not found.'}, status=404)
                return response


            # Check if the user comment exist in product
            # user_comment_in_product = session.query(ProductComment).filter(and_(ProductComment.user_id=user_id , ProductComment.product_id=product_id))
            user_comment_in_product = session.query(ProductComment).filter_by(user_id=user_id , product_id=product_id).first()
            if user_comment_in_product:
                response = JsonResponse({'message': 'User comment already exist.'}, status=404)
                return response


            # Create a new comment object with the given parameters
            new_comment = ProductComment(
                user_id=user_id,
                product_id=product_id,
                ip=request.META.get('REMOTE_ADDR', ''),
                comment=comment_text,
                rate=rate,
                status='published'
            )

            # Add the new comment to the database and commit the changes
            session.add(new_comment)
            
            
        # Return a JSON response with a success message and the comment's information
        response = JsonResponse({'message': 'Comment added successfully.', 'comment_id': new_comment.id, 'user_id': user_id, 'product_id': product_id, 'comment': comment_text, 'rate': rate}, status=200)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails('Something went wrong when adding the comment.', e, 500)
        return response

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
        
        user_id = request.user.id
        comment_id = data.get('comment_id')
        comment = data.get('comment')
        rate = data.get('rate')
        status = data.get('status')
        
        if not (comment_id and comment and rate and status):
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. Comment ID, comment text, rate and status must be filled.'}, status=400)
            add_get_params(response)
            return response
        
        # Use session_scope to manage the database session
        with session_scope() as session:
            # Query the comment by ID
            comment_obj = session.query(ProductComment).filter_by(id=comment_id, user_id=user_id).first()
            if not comment_obj:
                response = JsonResponse({'answer':'False', 'message':'Comment not found or you do not have permission to this comment.'}, status=404)
                add_get_params(response)
                return response

            # Update the comment object with the new parameters
            comment_obj.comment = comment
            comment_obj.rate = rate
            comment_obj.status = status

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
        user_id = request.user.id
        comment_id = data.get('comment_id')

        if not (comment_id or user_id):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. Comment ID must be provided.'}, status=404)            
            add_get_params(response)
            return response
        
        with session_scope(bind=engine) as session:
            # Check if the comment exists
            comment_obj = session.query(ProductComment).filter_by(id=comment_id, user_id=user_id).first()
            if not comment_obj:
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
