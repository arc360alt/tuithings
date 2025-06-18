import random
import time

start_time = time.time()
genned = 0

print("-------------------------")
print(" Minecraft Seed Generator  ")
print("-------------------------")

time.sleep(2)

while time.time() - start_time < 8:
    a = random.randrange(-9223372036854775808, 9223372036854775808)
    genned += 1
    print(a)

print(f"Generated {genned} seeds in {time.time() - start_time - 2:.2f} seconds.")