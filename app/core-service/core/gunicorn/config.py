bind = '0.0.0.0:8080'

access_log_format = "%(h)s | %(r)s %(s)s"
accesslog = '-'

# workers = 2
threads = 2
reload = False

# reload_engine = 'inotify'

# threads = 10

# max_requests = 1

# worker_class = 'core.CustomWorker'

# access_log_format': "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"

# daemon = True

# preload_app = False

# print_config = True

# wsgi_app = 'run:app'


from atexit import unregister
from multiprocessing.util import _exit_function


def post_worker_init(worker):
    
    # print("GUNICORN post_worker_init")
    
    unregister(_exit_function)
    print(f"GUNICORN Worker  {worker.pid} _exit_function unregitered")
    

def worker_int(worker):
    
    # print("GUNICORN worker_int")
    
    print(f"GUNICORN Worker received INT or QUIT signal {worker.pid}")

    from core import app
    
    runner = app.config['RUNNER']
    runner.stop()
    
    print(f"GUNICORN Runner stopped: {runner}")
    
    print_threads_traceback()


def worker_abort(worker):
    print(f"GUNICORN worker_abort - worker received SIGABRT signal {worker.pid}")
    
    
def print_threads_traceback():
    
    print("Threads traceback:")

    import threading, sys, traceback
    
    threads_dict = {thread.ident: thread.name for thread in threading.enumerate()}
    code = []
    
    for thread_id, stack in sys._current_frames().items():
        
        thread_name = threads_dict.get(thread_id,"")
        
        thread_line = f"\nThread: {thread_name}({thread_id})\n"
        
        code.append(thread_line)
        
        for filename, line_number, module, line in traceback.extract_stack(stack):
            code.append(f'File: "{filename}", line {line_number}, in {module}')
            if line:
                code.append(f"  {line.strip()}")

    print("\n".join(code))
    
    
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
    