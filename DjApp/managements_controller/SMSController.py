from django.http import JsonResponse
from twilio.rest import Client
from DjAdvanced.settings.production import auth_token, account_sid, verify_sid
from django.views.decorators.csrf import csrf_exempt
from DjApp.decorators import login_required, require_http_methods
from DjAdvanced.settings.production import engine


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_verification_code_with_twilio(request):
    # Download the helper library from https://www.twilio.com/docs/python/install

    # Set environment variables for your credentials
    # Read more at http://twil.io/secure

    verified_number = request.user.telephone

    client = Client(account_sid, auth_token)

    verification = client.verify.v2.services(verify_sid) \
        .verifications \
        .create(to=verified_number, channel="sms")

    print(verification.status)

    return JsonResponse({"message": verification.status}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def verify_twilio(request):
    session = request.session

    # decode the token to retrieve the user's id
    client = Client(account_sid, auth_token)
    person = request.person
    country_phone_code = person.phone_number_id[0].country_phone_code
    verified_number = str(country_phone_code) + \
        str(person.phone_number_id[0].phone_number)

    data = request.data
    otp_code = data.get('otp_code')

    verification_check = client.verify.v2.services(verify_sid) \
        .verification_checks \
        .create(to=verified_number, code=otp_code)

    if verification_check.status != "Approved":
        return JsonResponse(
            {
                "answer": "False",
                "message": "The verification code is incorrect.",
                "verification_check.status": verification_check.status,
            },
            status=400,
        )
    person.phone_verify = True
    return JsonResponse(
        {
            "answer": "True",
            "message": "Your phone number has been verified successfully.",
            "verification_check.status": verification_check.status,
        },
        status=200,
    )

    # print(verification_check.send_code_attempts)
