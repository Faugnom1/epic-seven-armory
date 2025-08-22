# backend/scripts/update_profile_legacy.py
# Back-compat profile updater at POST /update_profile
# - Works with/without Authorization header.
# - Accepts both "streamer_name" and legacy "straemer_name".
# - Returns {success, profile_completed}.

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import jwt

UPDATE_BP = Blueprint("update_profile_legacy", __name__)

def _profile_completed(doc: dict) -> bool:
    return all(bool(str(doc.get(k, "")).strip())
               for k in ("epic_seven_account", "streamer_name", "rta_rank"))

@UPDATE_BP.route("/update_profile", methods=["POST", "OPTIONS"])
def update_profile():
    # Handle CORS preflight explicitly if it hits this route
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}

    # Prefer user from app JWT if provided
    users = current_app.config["USERS_COLLECTION"]
    query = None

    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("sub")
            # Try ObjectId if available; otherwise fall back to plain string match
            obj_id = current_app.config.get("ObjectId")
            query = {"_id": obj_id(user_id)} if obj_id else {"_id": user_id}
        except Exception:
            # If token invalid, fall back to username below
            query = None

    if query is None:
        # Legacy behavior: identify by username sent from client
        username = str(data.get("username", "")).strip()
        if not username:
            return jsonify({"success": False, "error": "missing_username"}), 400
        query = {"username": username}

    # Build update set
    epic = str(data.get("epic_seven_account", "")).strip()
    stream = str(data.get("streamer_name") or data.get("straemer_name") or "").strip()
    rta = str(data.get("rta_rank", "")).strip()

    update_fields = {
        "epic_seven_account": epic,
        "streamer_name": stream,
        "rta_rank": rta,
        "updated_at": datetime.utcnow(),
    }

    res = users.update_one(query, {"$set": update_fields})
    if not res.matched_count:
        return jsonify({"success": False, "error": "user_not_found"}), 404

    user = users.find_one(query)
    return jsonify({
        "success": True,
        "profile_completed": _profile_completed(user),
    }), 200

def register_update_profile_legacy(app, *, users_collection, object_id_cls=None):
    app.config["USERS_COLLECTION"] = users_collection
    if object_id_cls:
        app.config["ObjectId"] = object_id_cls
    app.register_blueprint(UPDATE_BP)
