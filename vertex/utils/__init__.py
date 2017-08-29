# from django.core.cache import cache
# from django.conf import settings

# def cache_result(timeout=settings.CACHES['default']['TIMEOUT']):
#     """
#     Tries to retrieve the value of `func` from the cache;
#     on miss, calls `func`, caches the result, and returns the result.
#
#     WARNING: cache invalidation must be implemented separately, or values cached
#     by this function will persist indefinitely.
#     """
#     def inner_decorator(func):
#         def get_from_cache_or_compute(instance, *args, **kwargs):
#             cache_key = '{app}_{model}_{name}_{id}'.format(
#                 app=instance._meta.app_label,
#                 model=instance._meta.model_name,
#                 name=func.__name__,
#                 id=instance.id
#             )
#             result = cache.get(cache_key)
#             if result is None:
#                 result = func(instance, *args, **kwargs)
#                 cache.set(cache_key, result, timeout=timeout)
#             return result
#         return get_from_cache_or_compute
#     return inner_decorator


def sizeof_fmt(num, boundary=1024, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < float(boundary):
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= float(boundary)
    return "%.1f%s%s" % (num, 'Y', suffix)
