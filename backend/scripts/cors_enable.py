# backend/scripts/cors_enable.py
from flask import request, make_response
from flask_cors import CORS

def enable_cors(app, origins=None, extra_headers=None):
    """
    Globally enable CORS and handle OPTIONS preflights.

    - origins: list of allowed dev origins
    - extra_headers: additional allowed headers (e.g., ["username"])
    """
    origins = origins or ["http://localhost:3000", "http://127.0.0.1:3000"]
    extra_headers = extra_headers or []
    default_allowed = ["Content-Type", "Authorization"] + list(extra_headers)

    # 1) Base CORS support
    CORS(
        app,
        resources={r"/*": {"origins": origins}},
        supports_credentials=True,
        expose_headers=["Content-Type"],
        allow_headers=default_allowed,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # 2) Add headers on every response (even errors)
    @app.after_request
    def _add_headers(resp):
        origin = request.headers.get("Origin")
        if origin in origins:
            # Basic CORS
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Credentials"] = "true"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"

            # If browser asked for specific headers in preflight, echo them back.
            requested = request.headers.get("Access-Control-Request-Headers")
            if requested:
                resp.headers["Access-Control-Allow-Headers"] = requested
            else:
                resp.headers["Access-Control-Allow-Headers"] = ", ".join(default_allowed)
        return resp

    # 3) Explicit OPTIONS handler, so every route has a preflight response
    @app.route("/<path:_any>", methods=["OPTIONS"])
    @app.route("/", methods=["OPTIONS"])
    def _options_preflight(_any=None):
        resp = make_response("", 204)
        return _add_headers(resp)
