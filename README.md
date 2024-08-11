# QueueFile

QueueFile is a basic file-based queue system for Python. It's designed for simplicity, not performance.

## Features

- File-based persistence
- Thread-safe operations
- Max queue size limit

## Installation

```
pip install queue-file
```

## Usage

```python
from queue_file import QueueFile

# Create a queue
q = QueueFile("/tmp/my_queue.txt", max_size=1000)

# Add items
q.enqueue("task1")
q.enqueue("task2")

# Get items
item = q.dequeue()  # Returns "task1"

# Check size
size = q.size()  # Returns 1

# Clear queue
q.clear()
```

## Limitations

- Not suitable for queues larger than 10,000 items
- Performance decreases with queue size

This project is released under the CC0 license, dedicating it to the public domain.