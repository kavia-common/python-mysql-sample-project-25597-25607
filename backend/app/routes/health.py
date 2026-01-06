from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("Health", "health", url_prefix="/", description="Health check routes")


@blp.route("/")
class HealthRoot(MethodView):
    def get(self):
        """Basic health endpoint (root)."""
        return {"message": "Healthy"}


@blp.route("/api/health")
class HealthApi(MethodView):
    def get(self):
        """Health endpoint under /api for consistent API base path usage."""
        return {"status": "ok"}
