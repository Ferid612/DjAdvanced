from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import permission_required, token_required
from DjApp.helpers import GetErrorDetails, add_get_params
from DjAdvanced.settings import engine
from .models import Users

@csrf_exempt
@token_required
# @permission_required(permission_name="read")
def get_user_data_by_username(request):

    try:
        
        
        Session = sessionmaker(bind=engine)
        session = Session()
        username= request.GET.get('username') or request.POST.get('username') 
        user = session.query(Users).filter_by(username=username).first()
        session.close()
        if user:
            user_data = {
                "id": user.id,
                "username": user.username,
                "_username": user.username,
                "usermail": user.usermail,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "telephone": user.telephone,
                "created_at": user.created_at,
                "modified_at": user.modified_at,
                "active": user.active,
                "phone_verify": user.phone_verify
            }
            response = JsonResponse(user_data,status=200)
            add_get_params(response)
            return response
        else:
            response = JsonResponse( {"error": "User not found"},status=200)
            add_get_params(response)
            return response
        
    except Exception as e:
        # Return a JSON response with an error message and the error details
    
        response = GetErrorDetails("An error occurred while getting user information.", e, 500)
        add_get_params(response)
        return response
