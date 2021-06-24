from itertools import combinations

target = 3

data = [12, 13, 4, 5, 17, 1, 2]

pairs = combinations(data, 2)

# result = next(((a, b) for a, b in pairs if a + b == target), None)

result = next(filter(lambda pair: sum(pair) == target, pairs), None)
    
print(result) if result else print("none")

