list = [1,2,3,4,5]
new_list = []

start = 1
stop = 4

# advance
print(list[start::stop])

# "normal"
for i in range(start, stop):
  new_list.append(list[i])
  
print(new_list)