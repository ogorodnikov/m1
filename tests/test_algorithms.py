import pytest

from functools import partial

from core.algorithms.egcd import egcd
from core.algorithms.bernvaz import bernvaz
from core.algorithms.grover import grover
from core.algorithms.grover_sudoku import grover_sudoku
from core.algorithms.dj import dj
from core.algorithms.simon import simon, simon_post_processing
from core.algorithms.qft import qft
from core.algorithms.qpe import qpe, qpe_post_processing
from core.algorithms.shor import shor


test_data = {
    
    egcd: {'a': '345', 'b': '455244237'},
    bernvaz: {'secret': '1010'},
    grover: {'secret_1': '10111', 'secret_2': '10101'},
    
    grover_sudoku: {'row_1': '10', 'row_2': '.1', 'width': 'autodetect', 'height': 'autodetect',
                    'maximum_digit': 'autodetect', 'solutions_count': 'autodetect',
                    'repetitions_limit': 'autodetect'},
                    
    partial(grover_sudoku): {'row_1': '10', 'row_2': '.1', 'width': '2', 'height': '2',
                             'maximum_digit': '1', 'solutions_count': '2',
                             'repetitions_limit': '3'},       
                             
    dj: {'secret': '1010'},
    
    simon: {'period': '1010', 'masquerade': 'True'},
    partial(simon): {'period': '0000', 'masquerade': 'True'},
    
    qft: {'number': '101'},
    qpe: {'angle': '0.25', 'precision': '3'},     
    shor: {'number': '330023'},
    partial(shor): {'number': '11'},
    partial(shor): {'number': '8'}
}

post_processing = {simon: simon_post_processing,
                   qpe: qpe_post_processing}

def log_stub(message):
    pass

dummy_counts = {'0': 0, '1': 1}


@pytest.mark.parametrize("runner_function, run_values", test_data.items())
def test_algorithm(runner_function, run_values):
    runner_function(run_values, log_stub)
    
    if runner_function in post_processing:
        post_processing_function = post_processing[runner_function]
        post_processing_function(dummy_counts, log_stub)