#!coding:utf8

from importlib import import_module

def load_class(class_path, *args, **kvargs):
    try:
        dot_idx = class_path.rfind('.')
        module_path = class_path[:dot_idx]
        class_name = class_path[dot_idx + 1:]
        module = import_module(module_path)
        obj = getattr(module, class_name)(*args, **kvargs)
    except (TypeError, ImportError):
        raise TypeError('确保类路径和参数正确')

    return obj


def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot+1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj
