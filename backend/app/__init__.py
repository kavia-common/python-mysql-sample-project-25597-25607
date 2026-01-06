from __future__ import annotations

from flask import Flask, request
from flask_cors import CORS
from flask_smorest import Api

from .routes.health import blp as health_blp
from .routes.users import blp as users_blp

app = Flask(__name__)
app.url_map.strict_slashes = False


def _allowed_origins() -> list[str]:
    """
    Build a pragmatic allowlist for CORS that works for both local dev and hosted previews.

    - Always allow localhost:3000 (React dev server).
    - Also allow the current request's Origin (if present) to support preview environments
      where the origin hostname is not known ahead of time.
    """
    origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
    origin = request.headers.get("Origin")
    if origin:
        origins.add(origin)
    return sorted(origins)


# CORS must allow the frontend dev server (localhost:3000) and the hosted preview origin.
# We avoid a blanket "*" here because browser credentialed requests won't work with "*" and
# because a narrow allowlist is safer for production parity.
CORS(
    app,
    resources={r"/*": {"origins": _allowed_origins()}},
)

# OpenAPI / Swagger UI (Flask-Smorest)
app.config["API_TITLE"] = "Sample Project Backend API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
# Swagger UI served at /docs
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(users_blp)
