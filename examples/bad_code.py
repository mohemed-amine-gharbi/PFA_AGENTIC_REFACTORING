import os
import os
import math

def f(a, b, c):
    if a > 10:
        if b > 5:
            if c < 3:
                print("ok")
            else:
                print("no")
        else:
            print("b small")
    else:
        print("a small")

def calculate(x):
    r = 0
    for i in range(50):
        r += i * x
    for i in range(50):
        r += i * x
    return r
