from gunicorn import glogging

bind = '0.0.0.0:8080'

accesslog = '-'
access_log_format = "GUNICO %(h)s: %(r)s %(s)s"

glogging.Logger.datefmt = "%Y-%m-%d %H:%M:%S"
glogging.Logger.error_fmt = "%(levelname).1s %(module)6.6s | %(message)s"
glogging.Logger.access_fmt = "%(levelname).1s %(module)6.6s | %(message)s"
glogging.Logger.syslog_fmt = "%(levelname).1s %(module)6.6s | %(message)s"

# syslog = True
# loglevel = 'info'
# capture_output = True
# disable_redirect_access_to_syslog = True

threads = 2

# workers = 2
# worker_class = 'core.CustomWorker'

# max_requests = 1

# daemon = True

# reload = False
# reload_engine = 'inotify'
# preload_app = False

# wsgi_app = 'run:app'

# print_config = True

# access_log_format': "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"


from atexit import unregister
from multiprocessing.util import _exit_function


# def post_worker_init(worker):
    # print("GUNICORN post_worker_init")
    # unregister(_exit_function)
    

# def worker_int(worker):
#     print(f"GUNICORN worker_int - worker received INT or QUIT signal {worker.pid}")

# def worker_abort(worker):
#     print(f"GUNICORN worker_abort - worker received SIGABRT signal {worker.pid}")

# def on_starting(server):
#     server.log.info("GUNICORN on_starting")

# def on_reload(server):
#     server.log.info("GUNICORN on_reload")
#     print("GUNICORN on_reload")

# def when_ready(server):
#     server.log.info("GUNICORN when_ready")

# def pre_fork(server, worker):
#     server.log.info("GUNICORN child_exit")
#     worker.log.info("GUNICORN child_exit")

# def post_fork(server, worker):
#     server.log.info("GUNICORN post_fork")
#     worker.log.info("GUNICORN post_fork")

# def pre_exec(server):
#     server.log.info("GUNICORN pre_exec")
#     print("GUNICORN pre_exec")

# def pre_request(worker, req):
#     print(f"GUNICORN pre_request {req.method} {req.path}")
    
# def post_request(worker, req, environ, resp):
#     print(f"GUNICORN post_request {req.method} {req.path}")
    
# def child_exit(server, worker):
#     server.log.info("GUNICORN child_exit")
#     worker.log.info("GUNICORN child_exit")

# def worker_exit(server, worker):
#     print("GUNICORN worker_exit")

# def nworkers_changed(server, new_value, old_value):
#     server.log.info("GUNICORN nworkers_changed")
    
# def on_exit(server):
#     server.log.info("GUNICORN on_exit")
#     print("GUNICORN on_exit")