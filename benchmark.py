import time
import os

from src.queue_file import QueueFile


def benchmark_enqueue(queue, num_items):
    start_time = time.time()
    for i in range(num_items):
        queue.enqueue(f"Task {i}")
    end_time = time.time()
    return end_time - start_time

def benchmark_dequeue(queue, num_items):
    start_time = time.time()
    for _ in range(num_items):
        queue.dequeue()
    end_time = time.time()
    return end_time - start_time

def run_benchmark(file_name, max_size, num_items):
    queue = QueueFile(file_name, max_size=max_size)
    
    enqueue_time = benchmark_enqueue(queue, num_items)
    dequeue_time = benchmark_dequeue(queue, num_items)
    
    print(f"Benchmark results for {num_items} items:")
    print(f"Enqueue time: {enqueue_time:.4f} seconds")
    print(f"Dequeue time: {dequeue_time:.4f} seconds")
    print(f"Enqueue throughput: {num_items/enqueue_time:.2f} items/second")
    print(f"Dequeue throughput: {num_items/dequeue_time:.2f} items/second")
    print()

    # Clean up
    os.remove(file_name)

if __name__ == "__main__":
    sizes = [100, 1000, 10000]
    for size in sizes:
        print(f"Running benchmark for queue size: {size}")
        path = f"/dev/shm/benchmark_queue_{size}.txt"
        run_benchmark(path, max_size=size, num_items=size)