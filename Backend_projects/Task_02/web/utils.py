'''Utility function for performing basic arithmetic operations.

This function takes two numeric values and a string representing
the operation to perform ('add', 'subtract', 'multiply', 'divide').

Returns:
    Tuple: A dictionary with the result or error message, and an HTTP status code.
'''

def perform_operation(x, y, op):
    try:
        # Convert inputs to float
        x = float(x)
        y = float(y)

        if op == "add":
            return {"result": x + y}, 200
        elif op == "subtract":
            return {"result": x - y}, 200
        elif op == "multiply":
            return {"result": x * y}, 200
        elif op == "divide":
            if y == 0:
                return {"error": "Cannot divide by zero"}, 400
            return {"result": x / y}, 200
        else:
            return {"error": "Invalid operation"}, 400

    except ValueError:
        return {"error": "Invalid input. Numbers required."}, 400
