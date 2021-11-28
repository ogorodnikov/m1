from qiskit import Aer
from qiskit import execute

from shor import Shor


shor = Shor()

number = 15
base = 2

print(f"SHOR number: {number}")
print(f"SHOR base: {base}")
    
circuit = shor.create_shor_circuit(number=number, 
                                   base=base, 
                                   task_log=print)

backend = Aer.get_backend('aer_simulator')

job = execute(circuit, backend, shots=1024)

counts = job.result().get_counts()        

run_data = {'Result': {'Counts': counts}, 
            'Run Values': {'number': number, 'base': base}}

shor.shor_post_processing(run_data=run_data, task_log=print)