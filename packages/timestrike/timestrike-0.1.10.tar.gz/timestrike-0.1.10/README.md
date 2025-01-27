# Timestrike

Python library for timing attacks

## Usage

The library provides two functions: `get_length` to obtain the length of the key, and `get_key` to obtain its content. They only require the user to define the function that gives the processing time of a given string.

## Examples

```
import socket
import time
from timestrike import get_key

def measure_time(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 1337))
        s.sendall(message.encode())
        start_time = time.time()
        s.recv(1024)
        end_time = time.time()
        response_time = end_time - start_time
        s.close()
        return response_time

k = get_key(measure_time, sample=3)
print(k)
```
