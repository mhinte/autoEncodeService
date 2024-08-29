def find(list, filter):
    for x in list:
        if filter(x):
            return x
    return False
