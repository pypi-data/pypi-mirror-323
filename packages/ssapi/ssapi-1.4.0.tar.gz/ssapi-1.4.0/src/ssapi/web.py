import os
import pkg_resources
from ast import literal_eval
from datetime import date, timedelta

from bottle import (
    get,
    post,
    put,
    route,
    request,
    response,
    default_app,
    Bottle,
)

from ssapi import defaults
from ssapi.entities import Sale, Return
from ssapi.env import get_env_database
from ssapi.names import RouteNames
from ssapi.types import Undefined
from ssapi.web_tools import get_bottle_routes
from ssapi.web_decorators import (
    accepts_json,
    returns_json,
    handles_db_errors,
    enables_cors,
    protected,
    not_cacheable
)


def get_application() -> Bottle:
    """Get the WSGI application"""
    return default_app()


@route(r"/<url:re:.*>", method="OPTIONS", name=RouteNames.CORS_PREFLIGHT)
@enables_cors
@protected
def options_preflight(*args, **kwargs):
    return None


@get("/")
@returns_json
@enables_cors
def get_root():
    app = get_application()
    routes = get_bottle_routes(app)
    pkg_version = pkg_resources.get_distribution("ssapi").version
    return {"version": pkg_version, "resources": routes}


@get("/shops")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_shops():
    return list(get_env_database().get_shops())


@get("/sales")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_sales():
    query = request.query.decode()
    start = query.get("start", None)
    end = query.get("end", None)
    shop = query.get("shop", None)
    is_discounted = query.get("isDiscounted", None)
    return [
        dict(sale.as_map())
        for sale in get_env_database().get_sales(
            date_start=start,
            date_end=end,
            shop=shop,
            is_discounted=(
                Undefined()
                if is_discounted is None
                else literal_eval(is_discounted)
            ),
        )
    ]


@get("/sales/<id:int>")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_sale(id: int) -> dict:
    sale = get_env_database().get_sale(id)
    if sale:
        return dict(sale.as_map())
    else:
        response.status = 404
        return {"outcome": f"not found: {request.path}"}


@put("/sales/<id:int>")
@accepts_json
@enables_cors
@protected
@not_cacheable
def put_sale(id: int) -> dict:
    # TODO: check id
    data = request.adapted_json
    data["id"] = id
    new_sale = Sale(**data)
    get_env_database().put_sale(id, new_sale)
    response.status = 204
    return {"outcome": f"update succeeded for sale {id}"}


@get("/returns")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_returns():
    query = request.query.decode()
    start = query.get("start", None)
    end = query.get("end", None)
    shop = query.get("shop", None)
    return [
        dict(sale.as_map())
        for sale in get_env_database().get_returns(
            date_start=start, date_end=end, shop=shop
        )
    ]


@get("/returns/<id:int>")
@returns_json
@protected
@not_cacheable
def get_return(id: int) -> dict:
    return_ = get_env_database().get_return(id)
    if return_:
        return dict(return_.as_map())
    else:
        response.status = 404
        return {"outcome": f"not found: {request.path}"}


@put("/returns/<id:int>")
@accepts_json
@enables_cors
@handles_db_errors
@protected
def put_return(id: int) -> dict:
    # TODO: check id
    data = request.adapted_json
    data["id"] = id
    new_return = Return(**data)
    get_env_database().put_return(id, new_return)
    response.status = 204
    return {"outcome": f"update succeeded for return {id}"}


@post("/sales")
@accepts_json
@returns_json
@handles_db_errors
@enables_cors
@protected
def post_sales():
    try:
        new_sale = Sale(**request.adapted_json)
    except TypeError as exc:
        response.status = 400
        outcome = (
            f"creation failed: "
            f"invalid parameters for type 'sale': "
            f"{request.json} {exc}"
        )
    else:
        db = get_env_database()
        count = db.add_sales(new_sale)
        outcome = f"creation ({count}) succeeded in database at: {db.name}"

    return {"outcome": outcome}


@post("/returns")
@accepts_json
@returns_json
@handles_db_errors
@enables_cors
@protected
def post_returns():
    try:
        new_return = Return(**request.adapted_json)
    except TypeError as exc:
        response.status = 400
        outcome = (
            f"creation failed: "
            f"invalid parameters for type 'sale': "
            f"{request.json} {exc}"
        )
    else:
        db = get_env_database()
        count = db.add_returns(new_return)
        outcome = f"creation ({count}) succeeded in database at: {db.name}"

    return {"outcome": outcome}


@get("/products")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_products():
    return tuple(get_env_database().get_products())


@post("/drop")
@returns_json
@enables_cors
@protected
def drop():
    # FIXME: add security
    db = get_env_database()
    db.drop()
    try:
        return {"outcome": f"Database dropped at: {db.name}"}
    finally:
        db.open()


@put("/settings/<owner_id>")
@accepts_json
@returns_json
@enables_cors
@protected
def put_settings(owner_id):
    data = request.adapted_json
    db = get_env_database()
    db.put_settings(owner_id, data)
    return {"outcome": f"Settings updated successfully at: {db.name}"}


@get("/settings/<owner_id>")
@returns_json
@enables_cors
@protected
@not_cacheable
def get_settings(owner_id):
    data = get_env_database().get_settings(owner_id)
    if data is None:
        response.status = 404
        return {"outcome": f"failed - owner '{owner_id}' not found"}
    else:
        return data


@get("/auth/<challenge_secret>")
@returns_json
@not_cacheable
def get_auth(challenge_secret: str):
    """Secret authentication URL"""
    secret = os.environ.get(defaults.DEFAULT_AUTH_SECRET_ENV_VAR, None)
    if secret is None:
        response.status = 503
        return {"reason": "Secret not set"}
    else:
        if challenge_secret == secret:
            db = get_env_database()
            session_secret = db.create_session().secret
            expire_date = date.today() + timedelta(days=365)
            session_domain = os.environ.get(
                defaults.DEFAULT_HOST_ENV_VAR, "localhost"
            )
            response.set_cookie(
                "ssapi",
                session_secret,
                expires=expire_date,
                domain=session_domain,
                path="/",
            )
            response.status = 200
            return {
                "outcome": "Valid secret. Session authenticated succesfully."
            }
        else:
            response.status = 404
            return {"reason": "Secret not found"}
