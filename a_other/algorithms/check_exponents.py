
def check_exponents(self, number, task_log):
    
    task_log(f'SHOR check_exponents')
    task_log(f'SHOR number: {number}')
    
    for factor_p in range(2, int(number ** 0.5) + 1):

        task_log(f'SHOR factor_p: {factor_p}')  
        
        factor_q = factor_p
        
        product = 1
        
        while product < number:

            task_log(f'SHOR     factor_q: {factor_q}')

            product = factor_p * factor_q
            
            task_log(f'SHOR         product: {product}')
            
            if product == number:
                
                task_log(f'SHOR >>> found: {factor_p} * {factor_q} = {product}')
                
                return
            
            factor_q += 1