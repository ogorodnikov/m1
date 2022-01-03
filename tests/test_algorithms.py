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
from core.algorithms.teleport import teleport
from core.algorithms.shor import shor, shor_post_processing
from core.algorithms.counting import counting, counting_post_processing
from core.algorithms.bb84 import bb84, bb84_post_processing


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
    
    simon: {'period': '10101010', 'masquerade': 'True'},
    partial(simon): {'period': '0000', 'masquerade': 'True'},
    
    qft: {'number': '101'},
    qpe: {'angle': '0.25', 'precision': '3'},
    teleport: {'alpha': 'random', 'beta': 'random'},
    partial(teleport): {'alpha': '1j', 'beta': '0'},
    shor: {'number': '15', 'base': '2'},
    counting: {'precision': '4', 'secret_1': '1011', 'secret_2': '1010'},
    bb84: {'alice_bits': '10101', 'alice_bases': 'XXXZX', 
           'eve_bases': 'XZZZX', 'bob_bases': 'XXXZZ', 
           'sample_indices': '0, 2'},
    
}


post_processing = {simon: simon_post_processing,
                   qpe: qpe_post_processing,
                   shor: shor_post_processing,
                   counting: counting_post_processing,
                   bb84: bb84_post_processing}


@pytest.mark.parametrize("runner_function, run_values", test_data.items())
def test_algorithm(runner_function, run_values, test_run_data, stub):
    
    runner_function(run_values=run_values, task_log=stub)
    
    if runner_function in post_processing:
        
        post_processing_function = post_processing[runner_function]
        post_processing_function(run_data=test_run_data, task_log=stub)
        
        
def test_shor_modular_inverse_fail(stub):
    
    no_modular_inverse_run_values = {'number': '2', 'base': '2'}
    
    with pytest.raises(ValueError) as error:
        
        shor(run_values=no_modular_inverse_run_values, task_log=stub)
        
    assert "Modular inverse does not exist" in str(error.value)
        

###   Fixtures   ###

@pytest.fixture(scope="module")
def test_run_data():
    
    return {'Result': {'Counts': {'0': 0, '1': 1}}, 
            'Run Values': {'value_1': 1, 'value_2': 2, 'number': 15, 'base': 2, 
                           'precision': '4', 'secret_1': '1011', 'secret_2': '1010',
                           'alice_bits': '10101', 'alice_bases': 'XXXZX', 
                           'eve_bases': 'XZZZX', 'bob_bases': 'XXXZZ', 
                           'sample_indices': '0',
            }}