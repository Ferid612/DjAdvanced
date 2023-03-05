import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
from DjApp.decorators import require_http_methods


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def get_person_location(request):

    ip = get_client_ip(request)
    
    url = "https://ipinfo.io/"+ip+"/json?token=a83e585ed3bd5c"

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "countries-cities.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)
    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response



@csrf_exempt
@require_http_methods(["POST","GET"])
def image_search(request):

    search_text=request.data.get('search_text') 

 
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

    querystring = {"q":search_text,"pageNumber":"1","pageSize":"10","autoCorrect":"true"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }


    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response


@csrf_exempt
@require_http_methods(["POST","GET"])
def web_search(request):

    search_text=request.data.get('search_text') 
 
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"

    querystring = {"q":search_text,"pageNumber":"1","pageSize":"10","autoCorrect":"true"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }


    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response



@csrf_exempt
@require_http_methods(["POST","GET"])
def auto_complete(request):
    search_text=request.data.get('search_text') 

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/AutoComplete"

    querystring = {"text":search_text}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response


@require_http_methods(["POST","GET"])
@csrf_exempt
def spell_check(request):
    search_text=request.data.get('search_text') 

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/spelling/SpellCheck"

    querystring = {"text":"teylor swiift"}

    headers = {
        "X-RapidAPI-Key": "7723ac98efmsh8726f21fbcf453fp1020f6jsn62755c65ce60",
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    resp_text = response.text
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response



@csrf_exempt
@require_http_methods(["POST","GET"])
def get_countiries(request):
    search_text=request.data.get('search_text') 
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
    querystring = {"offset":"100"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    # response = requests.request("GET", url, headers=headers)

    print(response.text)

    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response


@csrf_exempt
@require_http_methods(["POST","GET"])
def get_cities(request):
    search_text=request.data.get('search_text') 
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

    response = requests.request("GET", url, headers=headers, params=querystring)
    resp_text = json.loads(response.text)
        
    response = JsonResponse({"ip_data": resp_text},status=200)
    
    return response
