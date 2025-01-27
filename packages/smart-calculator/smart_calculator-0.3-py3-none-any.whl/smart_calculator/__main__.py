import sys
from smart_calculator import add, sub, mult, div

def main():
    
    if len(sys.argv) < 2:
        print("Usage: smart_calculator <operation> <args>")
        sys.exit(1)

    operation = sys.argv[1]
    args = [float(arg) for arg in sys.argv[2:]]

    if operation == "add":
        print(add(*args))
    elif operation == "sub":
        print(sub(*args))
    elif operation == "mult":
        print(mult(*args))
    elif operation == "div":
        print(div(*args))
    else:
        print("Invalid operation. Use 'add', 'sub', 'mult' or 'div'.")
        sys.exit(1)
