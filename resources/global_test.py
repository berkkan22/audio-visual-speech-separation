array = 5

def test():
    global array
    array = [1, 2, 3]
    print("1", array)
    array.append(4)
    print("2", array)
    
test()
print("3", array)