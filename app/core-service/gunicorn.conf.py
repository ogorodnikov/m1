bind = '0.0.0.0:8080'

access_log_format = "%(h)s | %(r)s %(s)s"
accesslog = '-'

workers = 1
reload = True

reload_engine = 'inotify'


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


def on_starting(server):
    server.log.info("on_starting")
    print("on_starting")

def on_reload(server):
    server.log.info("on_reload")
    print("on_reload")

def when_ready(server):
    server.log.info("when_ready")
    print("when_ready")

def pre_fork(server, worker):
    server.log.info("child_exit")
    worker.log.info("child_exit")
    print("child_exit")

def post_fork(server, worker):
    server.log.info("post_fork")
    worker.log.info("post_fork")
    print("post_fork")

def post_worker_init(worker):
    worker.log.info("post_worker_init")
    print("post_worker_init")
    
    unregister(_exit_function)
    worker.log.info(f"Exit function unregistered for Worker {worker.pid}")
    print(f"Exit function unregistered for Worker {worker.pid}")

def worker_int(worker):
    worker.log.info("worker_int - worker received INT or QUIT signal")
    print("worker_int - worker received INT or QUIT signal")
    
    from core import app
    
    runner = app.config['RUNNER']
    
    print(f"Stopping runner: {runner}")
    
    runner.stop()
    
    # print_threads_traceback()


def worker_abort(worker):
    worker.log.info("worker_abort - worker received SIGABRT signal")
    print("worker_abort - worker received SIGABRT signal")

def pre_exec(server):
    server.log.info("pre_exec")
    print("pre_exec")

def pre_request(worker, req):
    worker.log.info(f"pre_request {req.method} {req.path}")
    print(f"pre_request {req.method} {req.path}")
    
def post_request(worker, req, environ, resp):
    worker.log.info(f"post_request {req.method} {req.path}")
    print(f"post_request {req.method} {req.path}")
    
def child_exit(server, worker):
    server.log.info("child_exit")
    worker.log.info("child_exit")
    print("child_exit")

def worker_exit(server, worker):
    server.log.info("worker_exit")
    worker.log.info("worker_exit")
    print("worker_exit")

def nworkers_changed(server, new_value, old_value):
    server.log.info("nworkers_changed")
    print("nworkers_changed")
    
def on_exit(server):
    server.log.info("on_exit")
    print("on_exit")
    
    
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
    