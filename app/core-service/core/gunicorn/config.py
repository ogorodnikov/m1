bind = '0.0.0.0:8080'

access_log_format = "%(h)s | %(r)s %(s)s"
accesslog = '-'

workers = 1
reload = True

# reload_engine = 'inotify'

# preload_app = False

# wsgi_app = 'run:app'

# max_requests = 1

# worker_class = 'core.CustomWorker'

# access_log_format': "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"


# threads = 10


# daemon = True

# print_config = True





# def post_fork(server, worker):
#     server.log.info("post_fork - Worker spawned (pid: %s)", worker.pid)

# def pre_fork(server, worker):
#     server.log.info("pre_fork S - Worker spawned (pid: %s)", worker.pid)
#     worker.log.info("pre_fork W - Worker spawned (pid: %s)", worker.pid)

# def pre_exec(server):
#     server.log.info("Forked child, re-executing.")


# from atexit import unregister
# from multiprocessing.util import _exit_function


# def when_ready(server):
#     server.log.info("Server is ready. Spawning workers")

# def worker_int(worker):
#     worker.log.info("worker received INT or QUIT signal")

#     ## get traceback info
#     import threading, sys, traceback
#     id2name = {th.ident: th.name for th in threading.enumerate()}
#     code = []
#     for threadId, stack in sys._current_frames().items():
#         code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""),
#             threadId))
#         for filename, lineno, name, line in traceback.extract_stack(stack):
#             code.append('File: "%s", line %d, in %s' % (filename,
#                 lineno, name))
#             if line:
#                 code.append("  %s" % (line.strip()))
#     worker.log.debug("\n".join(code))

# def worker_abort(worker):
#     worker.log.info("worker received SIGABRT signal")
    
# def on_reload(server):
#     print(f">>>> on_reload {server}")
    
# def on_starting(server):
#     print(f">>>> on_starting {server}")
    

# def post_worker_init(worker):
#     unregister(_exit_function)
#     worker.log.info(f"Exit function unregistered for Worker {worker.pid}")
    