import logging
import threading
import time


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
    
    

def launch_multiple_threads():

    threads = list()
    
    for index in range(3):
        
        logging.info("Main    : create and start thread %d.", index)
        
        x = threading.Thread(target=thread_function, args=(index,))
        
        threads.append(x)
        
        x.start()

    for index, thread in enumerate(threads):
        
        logging.info("Main    : before joining thread %d.", index)
        
        thread.join()
        
        logging.info("Main    : thread %d done", index)

    

if __name__ == "__main__":
    
    format = "%(asctime)s: %(message)s"
    
    logging.basicConfig(format=format, 
                        level=logging.INFO,
                        datefmt="%H:%M:%S")

    launch_multiple_threads()
    
    
    
