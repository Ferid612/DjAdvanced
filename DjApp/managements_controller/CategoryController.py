from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..decorators import permission_required, login_required, require_http_methods
from ..helpers import add_get_params
from ..models import Category, Product


@csrf_exempt
@require_http_methods(["POST"])
def add_category(request):
    """
    This function adds new categories to the 'category' table in the database.
    If a category with the same name already exists, it will not be added again.
    """
    data = request.data
    categories = data.get('categories')

    added_categories = []
    existing_categories = []

    session = request.session
    for category in categories:
        if (session.query(Category).filter_by(name=category).one_or_none()):
            existing_categories.append(category)
        else:
            new_category = Category(name=category)
            added_categories.append(category)
            session.add(new_category)  # add the new category to the session
            session.commit()    # commit the changes to the database

    response = JsonResponse({'existing_categories': existing_categories,
                            'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def add_subcategories(request, category_id):
    """
    This function adds a new child category to an existing parent category in the 'category' table in the database.
    If the parent category does not exist, the child category will not be added.
    """
    data = request.data
    subcategories = data.get('subcategories')

    session = request.session

    # check if the parent category exists
    parent_category = session.query(Category).get(category_id)
    if not parent_category:
        response = JsonResponse(
            {'message': f"Parent category '{category_id}' id does not exist"}, status=400)
        add_get_params(response)
        return response

    added_categories = []
    existing_categories = []

    for subcategory in subcategories:
        if (
            existing_category := session.query(Category)
            .filter_by(name=subcategory)
            .one_or_none()
        ):
            existing_categories.append(subcategory)
        else:
            new_category = Category(
                name=subcategory, parent_id=parent_category.id)
            added_categories.append(subcategory)
            session.add(new_category)

    session.commit()  # commit all changes to the database

    response = JsonResponse({'existing_categories': existing_categories,
                            'added_categories': added_categories}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
# @login_required
# @permission_required("Manage product categories")
def update_category(request, category_id):
    """
    This function updates an existing category in the 'category' table in the database.
    If the category does not exist, it will not be updated.
    """
    data = request.data
    new_name = data.get('name')
    new_parent_id = data.get('parent_id')
    new_icon = data.get('icon')

    session = request.session

    # check if the category exists
    category = session.query(Category).get(category_id)
    if not category:
        response = JsonResponse(
            {'message': f"Category '{category_id}' id does not exist"}, status=400)
        add_get_params(response)
        return response

    # update category attributes if provided
    if new_name is not None:
        category.name = new_name

    if new_parent_id is not None:
        # check if the new parent category exists
        parent_category = session.query(Category).get(new_parent_id)
        if not parent_category:
            response = JsonResponse(
                {'message': f"Parent category '{new_parent_id}' id does not exist"}, status=400)
            add_get_params(response)
            return response

        # check if the new parent category is not the same as the current parent category
        if category.parent_id != new_parent_id:
            category.parent_id = new_parent_id

    if new_icon is not None:
        category.icon = new_icon

    session.commit()  # commit the changes to the database

    # return the updated category as JSON
    updated_category = {
        'id': category.id,
        'name': category.name,
        'parent_id': category.parent_id,
        'icon': category.icon,
    }
    response = JsonResponse(updated_category, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST"])
def delete_category(request, category_id):
    """
    This function is used to delete a specific category.
    Parameters:
        category_id (int): The ID of the category to be deleted.
    """
    data = request.data
    session = request.session

    # Check if the category exists
    category = session.query(Category).get(category_id)
    if not category:
        response = JsonResponse(
            {'answer': f'No category found with category.id {category_id}'}, status=404)
        add_get_params(response)
        return response

    # Check if the category has any products
    if category.has_products():
        response = JsonResponse(
            {'answer': f'Cannot delete category with category.id {category_id}, it has products associated with it.'}, status=400)
        add_get_params(response)
        return response

    session.delete(category)
    response = JsonResponse(
        {'message': f'Category with category.id {category_id} has been successfully deleted.'}, status=200)
    add_get_params(response)
    return response


@csrf_exempt
@require_http_methods(["POST", "GET"])
def delete_null_category_products(request):
    """
    This function deletes all products that have a null category_id.
    """
    session = request.session
    # query to get all products that have a null category_id
    null_category_products = (
        session.query(Product).filter(Product.category_id is None).all()
    )
    # Iterate through the products and delete them one by one
    for product in null_category_products:
        session.delete(product)
        session.commit()
        print(
            f"Deleted {len(null_category_products)} products with null category_id")
        # Return the number of deleted products for confirmation

    response = JsonResponse({"message": "deleted all products that have a null category_id succesfully.",
                            "lentgth of null_category_products": len(null_category_products)}, status=200)
    add_get_params(response)
    return response
