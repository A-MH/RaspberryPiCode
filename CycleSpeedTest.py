import time

global counter
counter = 0
start_time = time.time()
for i in range(1000):
    counter = counter + 1
print (counter)
cycle = (time.time() - start_time) / 1000
print(cycle)