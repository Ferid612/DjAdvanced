from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect, render
from django.urls import reverse


def google_login_callback(request):

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": "1061024007426-37p2ccs7suqcb2s5cec4gn63j8v7h2s6.apps.googleusercontent.com",
                "client_secret": "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",
                "redirect_uri": "https://e-delta.store/google_auth/google-login-callback/",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "userinfo_uri": "https://openidconnect.googleapis.com/v1/userinfo",
                "scope": ["https://www.googleapis.com/auth/userinfo.email",  "https://www.googleapis.com/auth/userinfo.profile", "openid"],
            }
        },
        scopes=["https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile", "openid"],
        redirect_uri='https://e-delta.store' + reverse("google_login_callback"),
    )

    if "code" in request.GET:
        return _extracted_from_google_login_callback_27(flow, request)
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    return redirect(authorization_url)


# TODO Rename this here and in `google_login_callback`
def _extracted_from_google_login_callback_27(flow, request):
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Retrieve the user's profile information from Google
    id_info = id_token.verify_oauth2_token(
        credentials._id_token, Request(), credentials._client_id
    )
    email = id_info["email"]
    name = id_info["name"]

    # Save the user's credentials to the Django session
    request.session["google_credentials"] = credentials.to_json()

    return redirect("/")


def google_logout(request):
    request.session.pop("google_credentials", None)
    return redirect("/")
