import re
import collections
from os import environ

import bottle

from ssapi.names import RouteNames
from ssapi.defaults import (
    DEFAULT_ALLOWED_ORIGIN_ENV_VAR,
    DEFAULT_SSAPI_ALLOW_ORIGIN,
)

camel_case_rxp = re.compile(r"^(?P<minor>[a-z]+)(?P<major>[A-Z]{1}\w*)$")
cors_allowed_headers = (
    "Origin",
    "Content-Type",
    "Authorization",
    "Accept",
    "Cache-Control"
)
cors_allowed_methods = ("POST", "GET", "PUT", "OPTIONS", "DELETE")


def get_cors_allowed_origin() -> str:
    return environ.get(
        DEFAULT_ALLOWED_ORIGIN_ENV_VAR, DEFAULT_SSAPI_ALLOW_ORIGIN
    )


preflight_response_headers = (
    ("Access-Control-Allow-Methods", ", ".join(cors_allowed_methods)),
    ("Access-Control-Allow-Headers", ", ".join(cors_allowed_headers)),
    ("Access-Control-Allow-Credentials", "true"),
    ("Access-Control-Allow-Origin", get_cors_allowed_origin),
)


def populate_cors_response(response: bottle.Response) -> None:
    """Create a simple preflight response"""
    for key, obj in preflight_response_headers:
        response.add_header(key, obj() if callable(obj) else obj)


def camel_to_snake_case(data: dict):
    """Convert camelCase to snake_case"""
    new_data = {}
    for key, val in data.items():
        if matched := camel_case_rxp.match(key):
            minor, major = matched.groups()
            new_data[f"{minor}_{major.lower()}"] = val
        else:
            new_data[key] = val

    return new_data


def get_bottle_routes(app: bottle.Bottle) -> dict[str, list[str]]:
    """Convert a bottle instance to a map that describes its active routes"""
    ns: dict = collections.defaultdict(list)
    route: bottle.Route
    for route in app.routes:
        if route.name != RouteNames.CORS_PREFLIGHT:
            ns[route.rule] += [route.method]
    return ns
