import os
from null_object import Null

PRIORITY_SETTING_OBJECTS = []
SETTING_OBJECTS = []


def add_settings(settings, priority=False):
    """添加额外的settings对象。

    参数：
        settings: 字典类型或对象类型。
        priority: 布尔类型。True表示高优先级，可以重载env中的设定。False表示低优先级，可以被env中的设置重载。
    """
    if priority:
        if not settings in PRIORITY_SETTING_OBJECTS:
            PRIORITY_SETTING_OBJECTS.append(settings)
    else:
        if not settings in SETTING_OBJECTS:
            SETTING_OBJECTS.append(settings)


def clear_settings():
    for i in range(len(PRIORITY_SETTING_OBJECTS) - 1, -1, -1):
        del PRIORITY_SETTING_OBJECTS[i]
    for i in range(len(SETTING_OBJECTS) - 1, -1, -1):
        del SETTING_OBJECTS[i]


def get(key, default=None, aliases=None):
    """获取配置项。优先从环境变量中获取配置项。后面依次从其它配置源中获取。"""
    aliases = aliases or []
    if isinstance(aliases, str):
        aliases = [aliases]
    if isinstance(key, str):
        keys = [key]
    else:
        keys = key
    keys += aliases
    # 高优先级
    for settings in PRIORITY_SETTING_OBJECTS:
        for key in keys:
            if isinstance(settings, dict):
                value = settings.get(key, Null)
            else:
                value = getattr(settings, key, Null)
            if value is not Null:
                return value
    # env
    for key in keys:
        value = os.environ.get(key, Null)
        if value is not Null:
            return value
    # 普通级
    for settings in SETTING_OBJECTS:
        for key in keys:
            if isinstance(settings, dict):
                value = settings.get(key, Null)
            else:
                value = getattr(settings, key, Null)
            if value is not Null:
                return value
    return default
