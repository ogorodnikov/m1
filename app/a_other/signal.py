import signal


# https://stackoverflow.com/questions/492519/timeout-on-a-function-call


def plot_timeout_handler(signal_number, stack_frame):
    
    raise TimeoutError(f"Plot timeout: {PLOT_STATEVECTOR_TIMEOUT} seconds")
    
    
def plot_statevector_figure(task_id, statevector):
    
    signal.signal(signal.SIGALRM, plot_timeout_handler)

    signal.alarm(PLOT_STATEVECTOR_TIMEOUT)

    try:
        
        figure = plot_bloch_multivector(statevector)
        
        # time.sleep(10)
        
        task_log(task_id, f'RUNNER figure: {figure}')        
    
        figure_path = app.static_folder + f'/figures/bloch_multivector_task_{task_id}.png'
                    
        figure.savefig(figure_path, transparent=True, bbox_inches='tight')
        
    except TimeoutError as exception:
        
        task_log(task_id, exception)

    signal.alarm(0)