import logging
import threading
import time

import concurrent.futures


def thread_function(name):
    
    logging.info("Thread %s: starting", name)
    
    time.sleep(2)
    
    logging.info("Thread %s: finishing", name)
    

def launch_one_daemon_thread():
    
    logging.info("Main    : before creating thread")
    
    x = threading.Thread(target=thread_function, args=(1,), daemon=True)
    
    logging.info("Main    : before running thread")
    
    x.start()
    
    logging.info("Main    : wait for the thread to finish")
    
    x.join()
    
    logging.info("Main    : all done")
    
    

def launch_multiple_threads(thread_count):

    threads = list()
    
    for index in range(thread_count):
        
        logging.info("Main    : create and start thread %d.", index)
        
        x = threading.Thread(target=thread_function, args=(index,))
        
        threads.append(x)
        
        x.start()

    for index, thread in enumerate(threads):
        
        logging.info("Main    : before joining thread %d.", index)
        
        thread.join()
        
        logging.info("Main    : thread %d done", index)
        
        
def launch_thread_pool_executor(thread_count):

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        
        executor.map(thread_function, range(thread_count))

    

if __name__ == "__main__":
    
    format = "%(asctime)s: %(message)s"
    
    logging.basicConfig(format=format, 
                        level=logging.INFO,
                        datefmt="%H:%M:%S")

    launch_thread_pool_executor(3)
    
    
    
