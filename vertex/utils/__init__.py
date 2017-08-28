from autoslug.utils import crop_slug, get_uniqueness_lookups, slugify
from django.core.cache import cache
from django.conf import settings


def generate_unique_slug(field, instance, slug, manager, index_padding=3, force_index=True):
    """
    Generates unique slug by adding a number to given value until no model
    instance can be found with such slug. If ``unique_with`` (a tuple of field
    names) was specified for the field, all these fields are included together
    in the query when looking for a "rival" model instance.
    """

    original_slug = slug = crop_slug(field, slug)

    default_lookups = tuple(get_uniqueness_lookups(field, instance, field.unique_with))

    index = 1

    if not manager:
        manager = field.model._default_manager

    # keep changing the slug until it is unique
    while True:
        # find instances with same slug
        lookups = dict(default_lookups, **{field.name: slug})
        rivals = manager.filter(**lookups)
        if instance.pk:
            rivals = rivals.exclude(pk=instance.pk)

        if not rivals and not force_index:
            # the slug is unique, no model uses it
            return slug
        elif not force_index:
            # the slug is not unique; change once more
            index += 1

        # ensure the resulting string is not too long
        tail_length = len(field.index_sep) + len(str(index).zfill(index_padding))
        combined_length = len(original_slug) + tail_length
        if field.max_length < combined_length:
            original_slug = original_slug[:field.max_length - tail_length]

        # re-generate the slug
        slug = '{slug}{sep}{index:0{pad}d}'.format(
            slug=original_slug,
            sep=field.index_sep,
            index=index,
            pad=index_padding
        )
        # We reset the force_index value so that we can continue the lookups normally
        force_index = False
        # ...next iteration...


def slugify_spaceless(value):
    return slugify(value.replace(" ", "")).upper()


def cache_result(timeout=settings.CACHES['default']['TIMEOUT']):
    """
    Tries to retrieve the value of `func` from the cache;
    on miss, calls `func`, caches the result, and returns the result.

    WARNING: cache invalidation must be implemented separately, or values cached
    by this function will persist indefinitely.
    """
    def inner_decorator(func):
        def get_from_cache_or_compute(instance, *args, **kwargs):
            cache_key = '{app}_{model}_{name}_{id}'.format(
                app=instance._meta.app_label,
                model=instance._meta.model_name,
                name=func.__name__,
                id=instance.id
            )
            result = cache.get(cache_key)
            if result is None:
                result = func(instance, *args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
            return result
        return get_from_cache_or_compute
    return inner_decorator


def sizeof_fmt(num, boundary=1024, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < float(boundary):
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= float(boundary)
    return "%.1f%s%s" % (num, 'Y', suffix)
