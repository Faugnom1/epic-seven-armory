# backend/scripts/profile_read_legacy.py
# GET /profile  -> returns profile fields for the current user.
# Works with either:
#   - Authorization: Bearer <app JWT>   (preferred), or
#   - ?username=<name>                  (legacy fallback)
#
# Response: { success, profile: { username, epic_seven_account, streamer_name, rta_rank, profile_completed } }

from flask import Blueprint, request, jsonify, current_app
import jwt

PROFILE_READ_BP = Blueprint("profile_read_legacy", __name__)

def _profile_completed(doc: dict) -> bool:
    return all(bool(str(doc.get(k, "")).strip())
               for k in ("epic_seven_account", "streamer_name", "rta_rank"))

@PROFILE_READ_BP.route("/profile", methods=["GET", "OPTIONS"])
def get_profile():
    if request.method == "OPTIONS":
        return ("", 204)

    users = current_app.config["USERS_COLLECTION"]

    # Prefer JWT
    query = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("sub")
            obj_id = current_app.config.get("ObjectId")
            query = {"_id": obj_id(user_id)} if obj_id else {"_id": user_id}
        except Exception:
            query = None

    # Fallback by ?username=...
    if query is None:
        username = (request.args.get("username") or "").strip()
        if not username:
            return jsonify({"success": False, "error": "missing_username"}), 400
        query = {"username": username}

    user = users.find_one(query)
    if not user:
        return jsonify({"success": False, "error": "user_not_found"}), 404

    streamer = user.get("streamer_name") or user.get("straemer_name") or ""
    data = {
        "username": user.get("username", ""),
        "epic_seven_account": user.get("epic_seven_account", ""),
        "streamer_name": streamer,
        "rta_rank": user.get("rta_rank", ""),
        "profile_completed": _profile_completed(user),
    }
    return jsonify({"success": True, "profile": data}), 200

def register_profile_read_legacy(app, *, users_collection, object_id_cls=None):
    app.config["USERS_COLLECTION"] = users_collection
    if object_id_cls:
        app.config["ObjectId"] = object_id_cls
    app.register_blueprint(PROFILE_READ_BP)
