import json
import os
import sqlite3
import logging
from functools import wraps
from http.cookies import SimpleCookie

from bottle import request, response

from ssapi import defaults
from ssapi.defaults import DEFAULT_SSAPI_WEB_CONTENT_TYPE
from ssapi.env import get_env_database
from ssapi.web_tools import camel_to_snake_case, populate_cors_response

_log = logging.getLogger(__name__)


def accepts_json(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs):
        content_type = request.headers.get("content-type", None)
        if content_type in (DEFAULT_SSAPI_WEB_CONTENT_TYPE, None):
            if isinstance(request.json, dict):
                try:
                    request.adapted_json = camel_to_snake_case(request.json)
                except json.JSONDecodeError as exc:
                    response.status = 400
                    return {"outcome": f"error: invalid JSON: {exc}"}
            else:
                request.adapted_json = request.json
        else:
            response.status = 400
            return {"outcome": "error: accepts only application/json"}

        return callable(*args, **kwargs)

    return wrapper


def returns_json(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs) -> str:
        response.content_type = DEFAULT_SSAPI_WEB_CONTENT_TYPE
        return json.dumps(callable(*args, **kwargs))

    return wrapper


def handles_db_errors(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs):
        try:
            return callable(*args, **kwargs)
        except sqlite3.Error as err:
            response.status = 500
            return {"outcome": f"error: db: {err}"}

    return wrapper


def enables_cors(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs):
        populate_cors_response(response)
        if request.method == "OPTIONS":
            response.status = 200

        return callable(*args, **kwargs)

    return wrapper


def protected(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            _log.debug(
                "Authentication not required for incoming OPTIONS request."
            )
        elif os.environ.get(defaults.DEFAULT_AUTH_SECRET_ENV_VAR, False):
            session_secret = get_env_database().get_current_session().secret
            if session_secret is None:
                response.status = 403
                return {"reason": "Unauthenticated. Authenticate first."}
            else:
                cookie = SimpleCookie(request.cookies)
                try:
                    cookie_secret = cookie["ssapi"].value
                except KeyError:
                    response.status = 403
                    return {"reason": "Unauthenticated. Cookie not set."}
                except AttributeError:
                    response.status = 400
                    return {"reason": "Error. No value for cookie."}
                else:
                    if cookie_secret != session_secret:
                        response.status = 403
                        return {
                            "reason": "Authentication error: incorrect secret."
                        }
                    else:
                        _log.debug(
                            "Authenticated request for session %s",
                            cookie_secret,
                        )
        else:
            _log.warning("Authentication not set")

        return callable(*args, **kwargs)

    return wrapper


def not_cacheable(callable):
    @wraps(callable)
    def wrapper(*args, **kwargs) -> str:
        response.headers["Cache-Control"] = "no-cache, no-store"
        return callable(*args, **kwargs)

    return wrapper
