# app_scan_bootstrap.py
# Keeps your existing app.py intact. Imports it and attaches the scan blueprint.

from app import app  # your existing Flask app object
from scripts.scan_manager import register_blueprint

register_blueprint(app)

# Expose `app` for flask/uwsgi
if __name__ == "__main__":
    # If your app.py already runs the server, you can ignore this.
    # Otherwise, this lets you run:  python app_scan_bootstrap.py
    app.run(host="0.0.0.0", port=5000, debug=True)
