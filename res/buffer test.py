import numpy as np

buffer = np.zeros(10)

print(buffer)

# füllt jedes 2 element mit 5 auf
buffer[::2] = 5

# füllt die ersten 2 elemente mit 1 auf von 0 - 2
buffer[:2] = 1

# füllt die letzten 2 elemente mit 2 auf von 8 - 10
buffer[8:10] = 2


print(buffer)
