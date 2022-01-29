def qae(run_values, task_log):
    
    ''' https://qiskit.org/documentation/finance/tutorials/00_amplitude_estimation.html '''
    
    # Input
    
    input_probability = run_values.get('bernoulli_probability')
    probability = float(input_probability)
    
    # Logs
    
    task_log(f'QAE run_values: {run_values}')
    task_log(f'QAE probability: {probability}')