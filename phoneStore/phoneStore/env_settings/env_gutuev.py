import os
from .env_base import BASE_DIR

FINLI_ENV = 'ENV_GUTUEV'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'fin-li.local'
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
