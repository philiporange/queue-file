import unittest
import os

from src.queue_file import QueueFile


class TestQueueFile(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_queue.txt"
        self.queue = QueueFile(self.test_file, max_size=100)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_enqueue_dequeue(self):
        self.queue.enqueue("Task1")
        self.queue.enqueue("Task2")
        self.queue.enqueue("Task3")

        self.assertEqual(self.queue.dequeue(), "Task1")
        self.assertEqual(self.queue.dequeue(), "Task2")
        self.assertEqual(self.queue.dequeue(), "Task3")
        self.assertIsNone(self.queue.dequeue())

    def test_max_size(self):
        for i in range(100):
            self.queue.enqueue(f"Task {i}")

        with self.assertRaises(RuntimeError):
            self.queue.enqueue("One too many")

    def test_size(self):
        self.assertEqual(self.queue.size(), 0)
        self.queue.enqueue("Task1")
        self.assertEqual(self.queue.size(), 1)
        self.queue.enqueue("Task2")
        self.assertEqual(self.queue.size(), 2)
        self.queue.dequeue()
        self.assertEqual(self.queue.size(), 1)

    def test_clear(self):
        self.queue.enqueue("Task1")
        self.queue.enqueue("Task2")
        self.queue.clear()
        self.assertEqual(self.queue.size(), 0)
        self.assertIsNone(self.queue.dequeue())

    def test_persistence(self):
        self.queue.enqueue("Task1")
        self.queue.enqueue("Task2")

        # Create a new queue instance with the same file
        new_queue = QueueFile(self.test_file, max_size=100)
        self.assertEqual(new_queue.dequeue(), "Task1")
        self.assertEqual(new_queue.dequeue(), "Task2")


if __name__ == "__main__":
    unittest.main()
