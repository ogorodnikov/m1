# from core import app

# from core import gunicorn_app

# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')
    
# gunicorn_app.run()



# from subprocess import run

# run('pwd')

# # run("gunicorn /m1/app/core-service/run:app --config='python:core.gunicorn.config'")

# run(["source", "/home/ec2-user/environment/flask-env/bin/activate"])
# run(["bash", "/home/ec2-user/environment/m1/app/core-service/run.sh"])


import os, sys

from gunicorn.app.wsgiapp import WSGIApplication
 
# wsgi_app = WSGIApplication()
# wsgi_app.app_uri = 'core:app'
 
# wsgi_app.run()

# path = os.path.join(os.path.dirname(__file__), "run.py")

# print(path)

sys.argv = [sys.argv[0]] + ["--bind", "0.0.0.0:8080",
                            "--workers", "1",
                            "--threads", "1",
                            "--config", '/home/ec2-user/environment/m1/app/core-service/gunicorn.conf.py',
                            "--reload",
                            # "--config", "python:core.gunicorn.config",
                            "core:app",

                            # path,
                            ]
                            
print(f"sys.argv: {sys.argv}")

# WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
WSGIApplication("%(prog)s [OPTIONS]").run()

# from core import app