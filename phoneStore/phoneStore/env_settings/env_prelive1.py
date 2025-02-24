import os
from typing import List, Dict, Any
from pathlib import Path

# Показывает константу среды запуска для отладки работы окружения
PHONESTORE_ENV: str = 'ENV_PRELIVE1'

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
PHONESTORE_DIR: Path = BASE_DIR / 'phoneStore'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6z2tgaqqvzf5ciq%#(js@tfgklzoo&^0*x-l%5uq9yss^e_c#n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = False

ALLOWED_HOSTS: List[str] = ['prelive1.iphoneondon.ru']


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES: Dict[str, Any]

PHONESTONE_DB_TYPE_VALUES: List[str] = ['mysql', 'sqlite']
PHONESTORE_DB_TYPE_DEFAULT: str = 'sqlite'
PHONESTORE_DB_TYPE: str = str(os.environ.get('FINLI_DB_TYPE', PHONESTORE_DB_TYPE_DEFAULT)).upper()
phonestore_db_type_value: str = str(PHONESTORE_DB_TYPE).lower()

if phonestore_db_type_value not in PHONESTONE_DB_TYPE_VALUES:
    raise ValueError('Нет такой конфигурации базы данных: ' + phonestore_db_type_value)
else:
    # Настройка для sqlite3
    if phonestore_db_type_value == 'sqlite':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

    # Настройка для MySQL/MariaDB
    elif phonestore_db_type_value == 'mysql':

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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  # Включить SSL
EMAIL_HOST_USER = 'iphoneondon.ru@yandex.ru' # Почта Димы
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'azsmicznbijdllye'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
