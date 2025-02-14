import json
from uuid import uuid4
from functools import lru_cache, wraps
from django.conf import settings
from django.contrib.sites.models import Site

from paho.mqtt import publish

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

# The JSONEncoder from DRF handles quite a few types, so we default to that
# if available and if not fallback to the Django one which still handles some
# extra types
try:
    from rest_framework.utils.encoders import JSONEncoder
except ImportError:
    from django.core.serializers.json import DjangoJSONEncoder as JSONEncoder


__all__ = ["single", "json_payload"]


def json_payload(func):
    """
    Decorator to add json support to MQTT publish methods
    """

    @wraps(func)
    def __inner(*args, **kwargs):
        if "json" in kwargs:
            data = kwargs.pop("json")
            kwargs["payload"] = json.dumps(data, cls=JSONEncoder).encode("utf8")

        return func(*args, **kwargs)

    return __inner


@lru_cache(maxsize=1)
# def client_id():
#     return (get_current_site(None).domain + "-%d" % uuid.uuid4().int)[:32]
def client_id():
    try:
        # Sử dụng Site model thay vì RequestSite
        current_site = Site.objects.get_current()
        domain = current_site.domain
    except Site.DoesNotExist:
        # Sử dụng một giá trị mặc định nếu không thể lấy được domain
        domain = "default_domain"       

    return (domain + "-%d" % uuid4().int)[:32]


@json_payload
@wraps(publish.single)
def single(topic, **kwargs):
    """
    Wrapped version of single, supporting AUTH and json payload
    """
    if settings.MQTT_USER and settings.MQTT_PASS:
        kwargs["auth"] = {
            "username": settings.MQTT_USER,
            "password": settings.MQTT_PASS,
        }

    return publish.single(
        topic,
        client_id=client_id(),
        hostname=settings.MQTT_HOST,
        port=settings.MQTT_PORT,
        **kwargs,
    )
