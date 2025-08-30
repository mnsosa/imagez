from .main import app as cli_app
from .api import app as web_app


def run_web_app():
    web_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)