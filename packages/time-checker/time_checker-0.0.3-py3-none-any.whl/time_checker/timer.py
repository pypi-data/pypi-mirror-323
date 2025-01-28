import time
from contextlib import contextmanager

# Context manager for timing code blocks
@contextmanager
def time_block(name="Code block"):
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        print(f"{name} executed in {end_time - start_time:.4f} seconds")

# Function to time an entire script
def script_timer():
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"Script executed in {end_time - start_time:.4f} seconds")

# Decorator for timing functions
def time_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper
