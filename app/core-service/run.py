# from core import app
# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')

# from core import gunicorn_app
# gunicorn_app.run()


import os, sys
from gunicorn.app.wsgiapp import WSGIApplication

root_path = os.path.dirname(__file__)

config_path = os.path.join(root_path, "core", "gunicorn", "config.py")

run_options = ["--config", config_path, "core:app"]

sys.argv.extend(run_options)

WSGIApplication("%(prog)s [OPTIONS]").run()

