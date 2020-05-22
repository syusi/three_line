i = 1

def test():
    global i
    i = 4
    print(i)

def pp():
    print(i)
test()
pp()