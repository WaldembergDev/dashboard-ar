from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['tigrupoquality.pythonanywhere.com']

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('ENGINE_DB'),
        'NAME': os.getenv('NAME_DB'),
        'USER': os.getenv('USER_DB'),
        'PASSWORD': os.getenv('PASSWORD_DB'),
        'HOST': os.getenv('HOST_DB'),
        'PORT': os.getenv('PORT_DB'),
    }
}