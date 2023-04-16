from operator import and_
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, login_required, require_http_methods
from DjApp.helpers import GetErrorDetails, add_get_params
from ..models import  Person, Product, ProductComment, ProductEntry, ProductRate, ProductFag, Users
from DjAdvanced.settings import engine
import Levenshtein





@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_rate_to_product(request):
    """
    This function handles adding a rate to a product. It receives the following parameters from the request object:
    - user_id: the ID of the user who posted the rate
    - product_entry_id: the ID of the product_entry to which the rate is posted
    - rate_comment: the rate text
    - rate: the rating of the product
    If the rate is added successfully, the function returns a JSON response with a success message and the rate's information.
    If an error occurs during the rate creation process, the function returns a JSON response with an error message and the error details.
    """
    # Parse request data
    data = request.data
    session = request.session
    
    user_id = request.person.user[0].id
    product_entry_id = data.get('product_entry_id')
    rate_comment = data.get('rate_comment')
    rate = data.get('rate')


    product_entry = session.query(ProductEntry).get(product_entry_id)
    
    # Check if all required data is present
    missing_fields = []
    if not user_id:
        missing_fields.append('user_id')
    if not product_entry_id:
        missing_fields.append('product_entry_id')
    if not rate_comment:
        missing_fields.append('rate_comment')
    if not rate:
        missing_fields.append('rate')
    if not product_entry:
        missing_fields.append(f"product_entry of {product_entry_id}")

    if missing_fields:
        message = f'Missing data error. The following fields are required: {", ".join(missing_fields)}.'
        return JsonResponse({'message': message}, status=400)


    # Check if comment already exists, or return 404 error if found
    if session.query(ProductRate).filter_by(user_id=user_id, product_entry_id=product_entry_id).one_or_none():
        return JsonResponse({'message': 'User comment already exists.'}, status=404)

    # Create a new comment object with the given parameters
    new_comment = ProductRate(
        user_id=user_id,
        product_entry_id=product_entry_id,
        ip=request.META.get('REMOTE_ADDR', ''),
        rate_comment=rate_comment,
        status='published'
    )
    new_comment.rate = rate

    # Add the new comment to the database and commit the changes
    session.add(new_comment)
    
    
    # Return a JSON response with a success message and the comment's information
    response = JsonResponse({'message': 'Comment added successfully.', 'comment_id': new_comment.id, 'user_id': user_id, 'product_id': product_entry_id, 'comment': rate_comment, 'rate': rate}, status=200)
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_rate(request):
    """
    This function handles updating a rate on a product by ID.
    The function receives the following parameters from the request object:
    - rate_id: the ID of the rate to be updated
    - rate: the updated rate text
    - rate: the updated rating of the rate
    - status: the updated status of the rate (approved, rejected or pending)
    If the rate update is successful, the function returns a JSON response with a success message and the updated rate's information.
    If the specified rate ID does not exist, the function returns a JSON response with an error message and status code 404.
    If an error occurs during the rate update process, the function returns a JSON response with an error message and the error details.
    """
    try:
        # Get the parameters from the request object
        data = request.data
        session = request.session
        user_id = request.person.user[0].id
        rate_id = data.get('rate_id')
        rate_comment = data.get('rate')
        rate = data.get('rate')
        status = data.get('status')
        
        if not (rate_id and rate_comment and rate and status):
            response = JsonResponse({'answer': 'False', 'message': 'Missing data error. rate ID, comment text, rate and status must be filled.'}, status=400)
            add_get_params(response)
            return response
        

        # Query the comment by ID
        comment_obj = session.query(ProductRate).get(rate_id)
        if not (comment_obj and (rate.user_id == user_id)):
            response = JsonResponse({'answer':'False', 'message':'rate not found or you do not have permission to this comment.'}, status=404)
            add_get_params(response)
            return response

        # Update the comment object with the new parameters
        comment_obj.rate_comment = rate_comment
        comment_obj.rate = rate
        
        
        # Return a JSON response with a success message and the updated comment's information
        response = JsonResponse({'answer': 'True', 'message': 'rate has been successfully updated.', 'comment_id': comment_obj.id, 'rate_comment': comment_obj.rate_comment, 'rate': comment_obj.rate, 'status': comment_obj.status}, status=200)
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
def delete_rate(request):
    """
    This function handles the deletion of a product rate. The function receives the following parameters from the request object:
    - rate_id: the ID of the rate to delete.
    If the rate deletion is successful, the function returns a JSON response with a success message.
    If an error occurs during the rate deletion process, the function returns a JSON response with an error message and the error details.
    """
    try:
        data = request.data
        user_id = request.person.user[0].id
        rate_id = data.get('rate_id')
        session = request.session
    
        if not (rate_id and user_id):
            response = JsonResponse({'answer':'False', 'message':'Missing data error. rate ID must be provided.'}, status=404)            
            add_get_params(response)
            return response
        
        # Check if the rate exists
        rate_obj = session.query(ProductRate).get(rate_id)
        if not (rate_obj and (rate_obj.user_id == user_id)):
            response = JsonResponse({'answer':'False', 'message':'Comment not found or you do not have permission to this rate.'}, status=404)
            add_get_params(response)
            return response

        # Delete the rate from the database
        session.delete(rate_obj)

        # Return a JSON response with a success message
        response = JsonResponse({"Success":"Rate deleted successfully."}, status=200)
        add_get_params(response)
        return response

    except Exception as e:
        # Return a JSON response with an error message and the error details
        response = GetErrorDetails("Something went wrong when deleting the rate.", e, 404)
        add_get_params(response)
        return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
def add_fag(request):
    """
    API endpoint to add a fag to a product_entry.
    The request should contain the following parameters:
    - product_entry_id: the ID of the product_entry to add the fag to
    - question: the question of the fag
    - answer: the answer of the fag
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data
    
    # Get the parameters from the request
    product_entry_id = data.get('product_entry_id')
    question = data.get('question')
    answer = data.get('answer')

    # Get the product_entry associated with the specified product_entry ID
    product_entry = session.query(ProductEntry).get(product_entry_id)
    if not product_entry:
        # If the product_entry doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid product_entry id."}, status=400)
        
        return response

    # Create a new fag object and add it to the product
    fag = ProductFag(product_entry_id=product_entry.id, question=question, answer=answer, status='active')
    session.add(fag)

    # Return a success response
    response = JsonResponse(
        {"answer": "The fag has been added to the product_entry successfully.",
            "product_entry_id":product_entry.id,
            "fag_id":fag.id,
            "question":fag.question,
            "answer":fag.answer
            },
        status=200
    )

    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
def update_fag(request):
    """
    API endpoint to edit a fag of a product.

    Parameters:
    - request: the HTTP request object containing the following parameters:
        - fag_id: the ID of the fag to edit
        - question: the new question for the fag
        - answer: the new answer for the fag
        - status: the new status for the fag

    Returns:
    - a success response with a JSON object containing the updated fag's details, or an error response if the fag_id is invalid.
    """

    # Get the session and data from the request object
    session = request.session
    data = request.data
    
    # Extract the parameters from the request data
    fag_id = data.get('fag_id')
    question = data.get('question')
    answer = data.get('answer')
    status = data.get('status')

    # Get the fag object associated with the specified fag ID
    fag_obj = session.query(ProductFag).get(fag_id)
    if not fag_obj:
        # If the fag object doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid fag id."}, status=400)
        
        add_get_params(response)
        return response

    # Update the fag object with the new values
    fag_obj.question = question
    fag_obj.answer = answer
    fag_obj.status = status

    # Return a success response with the updated fag's details
    response = JsonResponse(
        {"answer": "The fag has been updated successfully.",
            "fag_id":fag_obj.id,
            "question":fag_obj.question,
            "answer":fag_obj.answer,
            "status":fag_obj.status
            
            },
        status=200
    )
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("manage_products")
def delete_fag(request):
    """
    API endpoint to delete a fag of a product.

    Parameters:
    - request: the HTTP request object containing the following parameters:
        - fag_id: the ID of the fag to delete

    Returns:
    - a success response indicating that the fag has been deleted, or an error response if the fag_id is invalid.
    """

    # Get the session and data from the request object
    session = request.session
    data = request.data
    
    # Extract the parameters from the request data
    fag_id = data.get('fag_id')
 
    # Get the fag object associated with the specified fag ID
    fag_obj = session.query(ProductFag).get(fag_id)
    if not fag_obj:
        # If the fag object doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid fag id."}, status=400)
        add_get_params(response)
        return response

    # Delete the fag object from the database
    session.delete(fag_obj)
    
    # Return a success response indicating that the fag has been deleted
    response = JsonResponse(
        {"answer": "The fag has been deleted successfully."},
        status=200
    )
    add_get_params(response)
    return response



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_comment(request):
    """
    API endpoint to add a comment to a product_entry.
    The request should contain the following parameters:
    - product_entry_id: the ID of the product_entry to add the comment to
    - person_id: the ID of the person who is posting the comment
    - comment_text: the text of the comment
    - parent_comment_id (optional): the ID of the parent comment (if any) for a nested comment
    """
    # Get the user object associated with the request
    session = request.session
    data = request.data
    person = request.person
    # Get the parameters from the request
    product_entry_id = data.get('product_entry_id')
    comment_text = data.get('comment_text')
    parent_comment_id = data.get('parent_comment_id')

    # Get the product_entry associated with the specified product_entry ID
    product_entry = session.query(ProductEntry).get(product_entry_id)
    if not product_entry:
        # If the product_entry doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid product_entry id."}, status=400)
        
        return response

    # Check if the user has already made a similar comment on this product_entry
    comments = session.query(ProductComment).filter_by(product_entry_id=product_entry.id, person_id=person.id).all()
    for c in comments:
        if Levenshtein.distance(comment_text, c.comment_text) <= len(comment_text) * 0.4:
            response = JsonResponse({'answer': "You have already made a similar comment on this product."}, status=400)
            return response

    # Create a new comment object and add it to the product
    comment = ProductComment(product_entry_id=product_entry.id, person_id=person.id, comment_text=comment_text, status='active')
    if parent_comment_id:
        # If a parent comment ID is provided, add the comment as a child of the parent comment
        parent_comment = session.query(ProductComment).get(parent_comment_id)
        if not parent_comment:
            # If the parent comment doesn't exist, return an error response
            response = JsonResponse({'answer': "Invalid parent comment id."}, status=400)
            
            return response
        
        comment.parent_comment_id = parent_comment.id


    session.add(comment)
    session.commit()
    # Return a success response
    response = JsonResponse(
        {"answer": "The comment has been added to the product_entry successfully.",
            
            "product_entry_id":product_entry.id,
            "comment_id":comment.id,
            "parent_comment_id":comment.parent_comment_id,
            "person_id":person.id,
            "person_username":person.username,
            "comment_text":comment.comment_text
            },
        status=200
    )

    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_comment(request):
    """
    API endpoint to update a comment for a product entry.

    Parameters:
    - request: the HTTP request object containing the following parameters:
        - comment_id: the ID of the comment to update
        - comment_text: the new text for the comment

    Returns:
    - a success response with a JSON object containing the updated comment's details, or an error response if the comment_id is invalid or the person making the request is not the same as the person who posted the comment.
    """

    # Get the session and data from the request object
    session = request.session
    data = request.data
    
    # Extract the parameters from the request data
    comment_id = data.get('comment_id')
    comment_text = data.get('comment_text')

    # Get the comment object associated with the specified comment ID
    comment_obj = session.query(ProductComment).get(comment_id)
    if not comment_obj:
        # If the comment object doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid comment id."}, status=400)
        add_get_params(response)
        return response

    # Check if the person making the request is the same as the person who posted the comment
    if comment_obj.person_id != request.person.id:
        # If not, return an error response
        response = JsonResponse({'answer': "You are not authorized to update this comment."}, status=401)
        add_get_params(response)
        return response

    # Update the comment object with the new text
    comment_obj.comment_text = comment_text

    # Return a success response with the updated comment's details
    response = JsonResponse(
        {"answer": "The comment has been updated successfully.",
            "comment_id":comment_obj.id,
            "product_entry_id":comment_obj.product_entry_id,
            "person_id":comment_obj.person_id,
            "comment_text":comment_obj.comment_text,
            "parent_comment_id":comment_obj.parent_comment_id,
            "status":comment_obj.status
            
            },
        status=200
    )
    add_get_params(response)
    return response




@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_comment(request):
    """
    API endpoint to delete a comment for a product entry.

    Parameters:
    - request: the HTTP request object containing the following parameters:
        - comment_id: the ID of the comment to delete

    Returns:
    - a success response with a JSON object containing the deleted comment's details, or an error response if the comment_id is invalid or the person making the request is not the same as the person who posted the comment.
    """

    # Get the session and data from the request object
    session = request.session
    data = request.data
    
    # Extract the parameters from the request data
    comment_id = data.get('comment_id')

    # Get the comment object associated with the specified comment ID
    comment_obj = session.query(ProductComment).get(comment_id)
    if not comment_obj:
        # If the comment object doesn't exist, return an error response
        response = JsonResponse({'answer': "Invalid comment id."}, status=400)
        add_get_params(response)
        return response

    # Check if the person making the request is the same as the person who posted the comment
    if comment_obj.person_id != request.person.id:
        # If not, return an error response
        response = JsonResponse({'answer': "You are not authorized to delete this comment."}, status=401)
        add_get_params(response)
        return response

    # Delete the comment object
    session.delete(comment_obj)

    # Return a success response with the deleted comment's details
    response = JsonResponse(
        {"answer": "The comment has been deleted successfully.",
            "comment_id":comment_obj.id,
            "product_entry_id":comment_obj.product_entry_id,
            "person_id":comment_obj.person_id,
            "comment_text":comment_obj.comment_text,
            "parent_comment_id":comment_obj.parent_comment_id,
            "status":comment_obj.status
            
            },
        status=200
    )
    add_get_params(response)
    return response

