# from core import app
# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')

# from core import gunicorn_app
# gunicorn_app.run()


import os, sys
from gunicorn.app.wsgiapp import WSGIApplication

root_path = os.path.dirname(__file__)

# sys.path.insert(0, root_path)

config_path = os.path.join(root_path, "core", "gunicorn", "config.py")
module_path = os.path.join(root_path, "application:app")

run_options = ["--config", config_path, "core.run.py"]

sys.argv.extend(run_options)

WSGIApplication("%(prog)s [APP_MODULE]").run()

