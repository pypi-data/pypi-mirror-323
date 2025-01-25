# PyCloudKit: A Toolkit for building Clouds with Python

## Description

PyCloudKit provides a toolkit for building clouds with Python. It includes:
* A server class for maintaining the cloud
* A client class for interacting with the cloud

## Features

*   Ease of use: PyCloudKit provides a simple interface for creating and managing clouds.
*   Reliability: PyCloudKit provides reliable integration with databases.
*   Speed: PyCloudKit provides fast cloud operations using asynchronous operations.

## Examples

### Simple cloud creation

```python
from PyCloudKit import CloudServer

server = CloudServer('127.0.0.1', 8080, 'databases/cloud.db')

def main():
    server.start()

if __name__ == '__main__':
    main()
```

### Connecting to the cloud

```python
from PyCloudKit import CloudClient

client = CloudClient('127.0.0.1', 8080)

def main():
    # Set value in cloud
    client.set('key', 'value')
    # Get value from cloud
    value = client.get('key')
    print(value)

if __name__ == '__main__':
    main()
```
# Installation

Pyserver can be installed using pip:

```bash
pip install PyCloudKit
```

# License

PyCloudKit is licensed under the MIT License. [GitHub](https://github.com/professionsalincpp/PyCloudKit/blob/main/LICENSE).