import os
from .env_base import BASE_DIR

PHONESTORE_ENV = 'ENV_GUTUEV'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
]

# Смысл данной логики в том, что при использовании DEBUG = True
# Django использует пременную STATICFILES_DIRS для поиска статических файлов
# При этом переменная STATIC_ROOT должна быть пустой, иначе выпадет ошибка
# Поэтому я задаю переменную STATICFILES_DIRS и делаю пустой STATIC_ROOT
# При DEBUG = False джанго смотрит на STATIC_ROOT, поэтому определяем её если условие не прошло

if DEBUG is True:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = ''
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  # Включить SSL
EMAIL_HOST_USER = 'stepnik0@yandex.ru' # Ваша почта Яндекс
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'dysmwqfrzkktfabk'  # Пароль от вашей почты
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
