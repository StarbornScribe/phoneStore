"""
Данный файл всего лишь управляет переопределением настроек через переменную окружения STORE_ENV
Базовые настройки см. env_settings/env_base.py
"""

import types
import importlib

# Тут происходит импорт настроек по конфигурации env_base
from phoneStore.phoneStore.env_settings.env_base import *

# Тут захардкожено значение по умолчанию, но по факту не важно, какое оно, т.к. все настройки PROD
# уже есть в env_settings/env_base.py

PHONESTORE_ENV_DEFAULT: str = 'base'
phonestore_env_value: str = str(os.environ.get('PHONESTORE_ENV', PHONESTORE_ENV_DEFAULT)).lower()

# Если не прод:
if phonestore_env_value != PHONESTORE_ENV_DEFAULT:

    # Определяем путь до файла, переопределяющего настройки согласно локальному окружению
    local_env_module_path: str = str(PHONESTORE_DIR) + '/env_settings/env_' + phonestore_env_value + '.py'

    # Если модуль найдет, импортируем настройки
    if os.path.exists(local_env_module_path):

        # Пытаемся импортировать параметры локального окружения
        local_env_module: types.ModuleType = importlib.import_module('phoneStore.env_settings.env_' + phonestore_env_value)

        # Импортируем все переопределенные константы в глобальный скоуп
        names: List[str] = []

        # Определяем перечень переменных окружения, переопределенных в локальной конфигурации
        if "__all__" in local_env_module.__dict__:
            names = local_env_module.__dict__['__all__']
        else:
            # otherwise we import all names that don't begin with _
            names = [x for x in local_env_module.__dict__ if not x.startswith("_")]

        # Если такие переменные есть, то обновляем их значение в глобальном списке переменных
        if len(names) > 0:
            globals().update({k: getattr(local_env_module, k) for k in names})

    else:
        raise ValueError('Нет такого окружения: ' + local_env_module_path)
