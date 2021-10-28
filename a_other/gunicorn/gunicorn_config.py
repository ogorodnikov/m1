# bind = os.getenv('WEB_BIND', '0.0.0.0:8000')
# accesslog = '-'
# access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"

# workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2))
# threads = int(os.getenv('PYTHON_MAX_THREADS', 1))

# reload = bool(strtobool(os.getenv('WEB_RELOAD', 'false')))



bind = '0.0.0.0:8080'

accesslog = '-'
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"

workers = 1
threads = 1

reload = 'true'




def worker_int(worker):
    
    print(f"GUNICORN Worker received INT or QUIT signal {worker.pid}")

    from core import app
    
    runner = app.config['RUNNER']
    runner.stop()
    
    print(f"GUNICORN Runner stopped: {runner}")
    
    print_threads_traceback()
    
    
    
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
    
    