from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import add_get_params
from ..models import Tag, ProductEntry, ProductTag


@csrf_exempt
@require_http_methods(["POST"])
def add_tag(request):
    """
    This function adds a new tag to the 'tag' table in the database.
    """
    session = request.session
    data = request.data
    name = data.get('name')
    description = data.get('description')

    if not name:
        response = JsonResponse(
            {'message': 'Please provide a name for the tag'}, status=400)
        add_get_params(response)
        return response

    existing_tag = session.query(Tag).filter_by(name=name).one_or_none()

    if existing_tag:
        response = JsonResponse(
            {'answer': 'False', 'message': 'Tag  with the given name already exists.'}, status=404)
        add_get_params(response)
        return response

    tag = Tag(name=name, description=description)
    session.add(tag)
    session.commit()
    response = JsonResponse(
        {'answer': "success", "tag": tag.to_json()}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def update_tag(request, tag_id):
    """
    This function updates an existing tag in the 'tag' table in the database.
    If the tag does not exist, it will not be updated.
    """
    data = request.data
    new_name = data.get('name')
    new_description = data.get('description')

    session = request.session

    # check if the tag exists
    tag = session.query(Tag).get(tag_id)
    if not tag:
        response = JsonResponse(
            {'message': f"Tag '{tag_id}' id does not exist"}, status=400)
        add_get_params(response)
        return response

    # update tag attributes if provided
    if new_name is not None:

        existing_tag = session.query(Tag).filter_by(
            name=new_name).one_or_none()

        if existing_tag:
            response = JsonResponse(
                {'answer': 'False', 'message': 'Tag  with the given name already exists.'}, status=404)
            add_get_params(response)
            return response

        tag.name = new_name

    if new_description is not None:
        tag.description = new_description

    session.commit()  # commit the changes to the database

    # return the updated tag as JSON
    updated_tag = {
        'id': tag.id,
        'name': tag.name,
        'description': tag.description,
    }
    response = JsonResponse(
        {'answer': 'Tag succesfully updated', 'updated_tag': updated_tag}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def delete_tag(request, tag_id):
    """
    This function is used to delete a specific tag.
    Parameters:
        tag_id (int): The ID of the tag to be deleted.
    """
    session = request.session

    # Check if the tag exists
    tag = session.query(Tag).get(tag_id)
    if not tag:
        response = JsonResponse(
            {'answer': f'No tag found with tag.id {tag_id}'}, status=404)
        add_get_params(response)
        return response

    session.delete(tag)
    response = JsonResponse(
        {'message': f'Tag with tag.id {tag_id} has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def add_tag_to_product_entry(request, entry_id):
    """
    This function adds a new tag to a specific product entry.
    Parameters:
        entry_id (int): The ID of the product entry to add the tag to.
    """
    session = request.session
    data = request.data
    tag_id = data.get('tag_id')

    # Check if the product entry exists
    product_entry = session.query(ProductEntry).get(entry_id)
    if not product_entry:
        response = JsonResponse(
            {'message': f"No product entry found with id {entry_id}"}, status=404)
        add_get_params(response)
        return response

    # Check if the tag exists
    tag = session.query(Tag).get(tag_id)
    if not tag:
        response = JsonResponse(
            {'message': f"No tag found with id {tag_id}"}, status=404)
        add_get_params(response)
        return response

    # Add the tag to the product entry
    product_entry.tags.append(tag)
    session.commit()

    response = JsonResponse(
        {'message': f"Tag '{tag.name}' added to product entry with id {product_entry.id}"}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def delete_tag_from_product_entry(request, entry_id):
    """
    This function deletes a tag from a specific product entry.
    Parameters:
        entry_id (int): The ID of the product entry to delete the tag from.
    """
    session = request.session
    data = request.data
    tag_id = data.get('tag_id')

    # Check if the product entry exists
    product_entry = session.query(ProductEntry).get(entry_id)
    if not product_entry:
        response = JsonResponse(
            {'message': f"No product entry found with id {entry_id}"}, status=404)
        add_get_params(response)
        return response

    # Check if the tag exists
    tag = session.query(Tag).get(tag_id)
    if not tag:
        response = JsonResponse(
            {'message': f"No tag found with id {tag_id}"}, status=404)
        add_get_params(response)
        return response

    # Remove the tag from the product entry
    if tag in product_entry.tags:
        product_entry.tags.remove(tag)
        session.commit()
        response = JsonResponse(
            {'message': f"Tag '{tag.name}' removed from product entry with id {product_entry.id}"}, status=200)
    else:
        response = JsonResponse(
            {'message': f"Product entry with id {product_entry.id} does not have tag '{tag.name}'"}, status=404)

    add_get_params(response)
    return response
