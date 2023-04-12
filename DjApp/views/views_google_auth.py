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
                "redirect_uri": "http://127.0.0.1:8000/google_auth/google-login-callback/",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "userinfo_uri": "https://openidconnect.googleapis.com/v1/userinfo",
                "scope": ["openid", "email", "profile"],
            }
        },
        scopes=["openid", "email", "profile"],
        redirect_uri='http://127.0.0.1:8000' + reverse("google_login_callback"),
    )

    if "code" not in request.GET:
        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )
        
        print("here we goooooooooooooooooo", authorization_url, state)
        return redirect(authorization_url)
    else:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        print("here we goooooooooooooooooo Againnnnnnnnnnnnnnnnnnnnn")

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
