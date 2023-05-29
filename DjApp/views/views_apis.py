import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
from DjAdvanced.settings.base import DATABASE_NAME
from DjApp.decorators import require_http_methods
from DjApp.helpers import django_logger


@csrf_exempt
def test_func(request):
    text = f"DB name is {DATABASE_NAME}."
    json_data = {"text_1":text}

    django_logger.info(text)
    return JsonResponse(json_data, status=200)

def test_func_error(request):
    text = f"DB name is {DATABASE_NAME}."
    json_data = {"text_1":text}

    django_logger.info(text)
    return JsonResponse(json_data, status=400)


def test_func_warning(request):
    text = f"DB name is {DATABASE_NAME}."
    json_data = {"text_1":text}

    django_logger.info(text)
    return JsonResponse(json_data, status=500)


def get_client_ip(request):
    return (
        x_forwarded_for.split(',')[0]
        if (x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'))
        else request.META.get('REMOTE_ADDR')
    )


@csrf_exempt
def get_person_location(request):

    ip = get_client_ip(request)

    url = f"https://ipinfo.io/{ip}/json?token=a83e585ed3bd5c"

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "countries-cities.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)
    

    


@csrf_exempt
@require_http_methods(["POST", "GET"])
def image_search(request):

    search_text = request.data.get('search_text')

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

    querystring = {"q": search_text, "pageNumber": "1",
                   "pageSize": "10", "autoCorrect": "true"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    print(response.text)
    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)

    

    


@csrf_exempt
@require_http_methods(["POST", "GET"])
def web_search(request):

    search_text = request.data.get('search_text')

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"

    querystring = {"q": search_text, "pageNumber": "1",
                   "pageSize": "10", "autoCorrect": "true"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    print(response.text)
    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)

    
    


@csrf_exempt
@require_http_methods(["POST", "GET"])
def auto_complete(request):
    search_text = request.data.get('search_text')

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/AutoComplete"

    querystring = {"text": search_text}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    print(response.text)
    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)

    


@require_http_methods(["POST", "GET"])
@csrf_exempt
def spell_check(request):
    search_text = request.data.get('search_text')

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/SpellCheck"

    querystring = {"text": "teylor swiift"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    resp_text = response.text

    return JsonResponse({"ip_data": resp_text}, status=200)

    


@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_countiries(request):
    search_text = request.data.get('search_text')
    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries"

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }

    # ! referential api
    # querystring = {"fields":"iso_a2,state_code,state_hasc,timezone,timezone_offset","iso_a2":"az","lang":"en","state_code":"US-CA","prefix":"san fr","limit":"250"}

    # headers = {
    #     "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
    #     "X-RapidAPI-Host": "referential.p.rapidapi.com"
    # }

    # ! referential state

    # url = "https://referential.p.rapidapi.com/v1/state"

    # querystring = {"fields":"iso_a2","name":"tex","iso_a2":"us","lang":"en","limit":"250"}

    # headers = {
    #     "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
    #     "X-RapidAPI-Host": "referential.p.rapidapi.com"
    # }

    # response = requests.request("GET", url, headers=headers, params=querystring)

    #! import requests
    # from requests.structures import CaseInsensitiveDict

    # url = "https://api.geoapify.com/v1/geocode/search?text=38%20Upper%20Montagu%20Street%2C%20Westminster%20W1H%201LJ%2C%20United%20Kingdom&apiKey=4cabd604471b4a3d8b5b5013b19da60d"

    # headers = CaseInsensitiveDict()
    # headers["Accept"] = "application/json"

    # resp = requests.get(url, headers=headers)

    # print(resp.status_code)
    querystring = {"offset": "100"}
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    # response = requests.request("GET", url, headers=headers)

    print(response.text)

    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)

    


@csrf_exempt
@require_http_methods(["POST", "GET"])
def get_cities(request):
    search_text = request.data.get('search_text')
    url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"

    querystring = request.data.get('querystring')

    # {
    # "querystring": {"limit":"5","countryIds":"AZ","namePrefix":"bak"},
    # "search_text":"search_text"
    # }

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    resp_text = json.loads(response.text)

    return JsonResponse({"ip_data": resp_text}, status=200)

    
