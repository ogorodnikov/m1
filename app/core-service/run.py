# from core import app

# from core import gunicorn_app

# app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True, reloader_type='stat')
    
# gunicorn_app.run()



# from subprocess import run

# run('pwd')

# # run("gunicorn /m1/app/core-service/run:app --config='python:core.gunicorn.config'")

# run(["source", "/home/ec2-user/environment/flask-env/bin/activate"])
# run(["bash", "/home/ec2-user/environment/m1/app/core-service/run.sh"])


# from gunicorn.app.wsgiapp import WSGIApplication
 
# wsgi_app = WSGIApplication()
# wsgi_app.app_uri = 'run:app'
 
# wsgi_app.run()


from core import app