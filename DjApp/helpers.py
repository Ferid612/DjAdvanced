from django.utils.html import escape
from django.http import JsonResponse
from sqlalchemy.orm import  sessionmaker
from contextlib import contextmanager
import json, traceback
from DjAdvanced.settings import engine



def GetErrorDetails(from_dev="Something went wrong.", e=Exception , status=400):
    error_data= {
        "From_dev":from_dev,
        "An exception occurred": str(e),
       "Type of exception": str(type(e)),
        "Exception message": str(e.args),
        "Traceback ":str(traceback.format_exc()),
    }
    traceback.print_tb(e.__traceback__)
    response = JsonResponse(error_data,status=status)
    return response


def add_get_params(resp):
    resp["Access-Control-Allow-Origin"] = "*"
    resp["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT"
    resp["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"





@contextmanager
def session_scope():
    
    session = sessionmaker(bind=engine)()
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except:
        raise
    finally:
        session.close()


def serializer(rows) -> list:
    "Return all rows from a cursor as a dict"
    return [dict(row) for row in rows]


def escape_dict(data):
    if isinstance(data, list):
        for x, l in enumerate(data):
            if isinstance(l, dict) or isinstance(l, list):
                escape_dict(l)
            else:
                if l is not None:
                    data[x] = escape(l)

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict) or isinstance(v, list):
                escape_dict(v)
            else:
                if v is not None:
                    data[k] = escape(v)
        return data


def escape_list(data):
    return list(map(lambda item: escape(item), data))


def input_json_sanitizer(request, parameter):
    if request.method == "GET":
        data = json.loads(request.GET.get(parameter))
    elif request.method == "POST":
        data = json.loads(request.POST.get(parameter))

    if isinstance(data, list):
        return escape_list(data)
    if isinstance(data, dict):
        return escape_dict(data)


def input_get_list_sanitizer(request, parameter):
    if request.method == "GET":
        data_list = request.GET.getlist(parameter)
    elif request.method == "POST":
        data_list = request.POST.getlist(parameter)

    return escape_list(data_list)

