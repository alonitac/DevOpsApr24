import math
import time

start_time = time.time()
count = 0

while True:
    math.factorial(100000)
    count += 1
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time >= 1:  # If one second has elapsed
        print("Calculations per second:", count)
        count = 0
        start_time = current_time