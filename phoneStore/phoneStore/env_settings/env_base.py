import os
from typing import List, Dict, Any
from pathlib import Path

# Показывает константу среды запуска для отладки работы окружения
PHONESTORE_ENV: str = 'ENV_BASE'

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
PHONESTORE_DIR: Path = BASE_DIR / 'phoneStore'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6z2tgaqqvzf5ciq%#(js@tfgklzoo&^0*x-l%5uq9yss^e_c#n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = False

ALLOWED_HOSTS: List[str] = ['iphoneondon.ru']


# Application definition

INSTALLED_APPS: List[str] = [
    'main',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE: List[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'phoneStore.middleware.CartMiddleware'
]

ROOT_URLCONF: str = 'phoneStore.urls'
TEMPLATE_DIR: str = os.path.join(BASE_DIR, 'templates')

TEMPLATES: List[Any] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION: str = 'phoneStore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES: Dict[str, Any]

FINLI_DB_TYPE_VALUES: List[str] = ['mysql', 'sqlite']
FINLI_DB_TYPE_DEFAULT: str = 'sqlite'
FINLI_DB_TYPE: str = str(os.environ.get('FINLI_DB_TYPE', FINLI_DB_TYPE_DEFAULT)).upper()
finli_db_type_value: str = str(FINLI_DB_TYPE).lower()

if finli_db_type_value not in FINLI_DB_TYPE_VALUES:
    raise ValueError('Нет такой конфигурации базы данных: ' + finli_db_type_value)
else:
    # Настройка для sqlite3
    if finli_db_type_value == 'sqlite':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

    # Настройка для MySQL/MariaDB
    elif finli_db_type_value == 'mysql':

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'iphone_on_don',
                'USER': 'iphone_on_don',
                'PASSWORD': 'bvz9g[X*plX.*bq9',
                'HOST': 'localhost',  # localhost - for unix-socket, 127.0.0.1 - for tcp/ip
                'PORT': '3306',
            }
        }
    else:
        raise ValueError('Возможно забыли добавить конфигурацию??')


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE: str = 'en-us'

TIME_ZONE: str = 'UTC'

USE_I18N: bool = True

USE_TZ: bool = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL: str = '/static/'
STATIC_ROOT: str = 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

SESSION_ENGINE = "django.contrib.sessions.backends.db"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  # Включить SSL
EMAIL_HOST_USER = 'stepnik0@yandex.ru' # Ваша почта Яндекс
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'dysmwqfrzkktfabk'  # Пароль от вашей почты
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER