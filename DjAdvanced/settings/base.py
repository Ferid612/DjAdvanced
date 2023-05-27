import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
BASE_DIR = Path(__file__).resolve().parent.parent.parent


SECRET_KEY = os.getenv("SECRET_KEY") or ""
MEDIA_ROOT = BASE_DIR / 'DjApp' / 'media'
PROFIL_IMAGE_ROOT = MEDIA_ROOT / 'profil_images'

# Password validation
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



DATABASE_NAME = os.getenv("DATABASE_NAME") 
DATABASE_USER = os.getenv("DATABASE_USER") 
DATABASE_SERVER = os.getenv("DATABASE_SERVER") 
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT") 

# DATABASE_NAME = "DeltaDB"
# DATABASE_USER = "postgres"
# DATABASE_SERVER = "deltadb-0.cepwuiqxjppx.eu-north-1.rds.amazonaws.com"
# DATABASE_PASSWORD = "Farid612"
# DATABASE_PORT = "5432"

# Password validation
EMAIL_HOST= os.getenv("EMAIL_HOST")
EMAIL_PORT= '587'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") 
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") 

account_sid = os.getenv("account_sid") 
auth_token = os.getenv("auth_token") 
verify_sid = os.getenv("verify_sid") 

SECRET_KEY = "django-insecure-v3!1=71op)$(g^fz+qw6wgvhpp%)%p(rd^zds5ul3j=vikj3pr"
DJANGO_SECRET_KEY = "km67%dzc7bl7ecii#%gn8q8*sc0_j2t4t$k0zjk5$#5e@lsj3b"

CLIENT_ORIGIN_URL = "http://localhost:4040"
PORT = "6060"
DEBUG_ENABLE = "false"

AUTH0_DOMAIN = "dev-xrvdjg4v1xa41kws.eu.auth0.com"
AUTH0_AUDIENCE = "https://delta.com"


# SQL Alchemy Configuration
def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    print(url)
    if not database_exists(url):
        create_database(url)
    return create_engine(url, pool_size=50, echo=False)


engine = get_engine(DATABASE_USER, DATABASE_PASSWORD, DATABASE_SERVER, DATABASE_PORT, DATABASE_NAME)

TENANT_ID = ""
CLIENT_ID = ""
SECRET = ""


EMAIL_USE_TLS=True      


# AUTH0
# AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
# AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
# AUTH0_CLIENT_ID="FKxBLxDlHpptOBG3oc0f5gRG1ys5svmx"
# AUTH0_DOMAIN="dev-xrvdjg4v1xa41kws.eu.auth0.com"


AUTH0_CLIENT_ID="ualhORzYGKAOIqk3yy9c0xVO0nNJHPuv"
APP_SECRET_KEY="ALongRandomlyGeneratedString"
AUTH0_CLIENT_SECRET="jPKrWxGTCzdPg8azDGqs4Sq0eZpKwBwgrPhOXGkoISzuf23mknxd7of_1KDsiwh0"
AUTH0_DOMAIN="dev-xrvdjg4v1xa41kws.eu.auth0.com"


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'DjApp',
    'DeltaConfApp'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjAdvanced.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjAdvanced.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        # 'NAME':DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_SERVER,
        'PORT': DATABASE_PORT,
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]




# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


