from django.shortcuts import redirect

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print(request.META['HTTP_HOST'])
        if request.META['HTTP_HOST'] == 'e-delta.shop':
            return redirect('https://www.e-delta.shop')
        return self.get_response(request)
