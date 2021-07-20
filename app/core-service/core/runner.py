from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz


runners = {'egcd': egcd,
           'bernvaz': bernvaz}
           
           
def run_algorithm(algorithm_id, run_values):
    
    # run_int_values = map(int, run_values)
    
    runner = runners[algorithm_id]
    
    run_result = runner(run_values)

    return run_result