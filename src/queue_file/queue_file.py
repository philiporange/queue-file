import fcntl
import jsonpickle
import os
import logging
import time
import errno
from typing import Any, Optional, Callable
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueFile:
    def __init__(
        self,
        filename: str = "/dev/shm/queue_file.jsonl",
        max_size: int = 1000000,
        timeout: float = 5.0,
    ):
        self.filename = filename
        self.max_size = max_size
        self.timeout = timeout
        if not os.path.exists(filename):
            with open(filename, "w"):
                pass

    @contextmanager
    def _locked_file(self, mode: str = "r+"):
        f = None
        start_time = time.time()
        try:
            f = open(self.filename, mode)
            while True:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    logger.debug(f"File {self.filename} locked successfully")
                    break
                except IOError as e:
                    if e.errno != errno.EAGAIN:
                        raise
                    elif time.time() - start_time > self.timeout:
                        raise TimeoutError(
                            f"Timeout waiting for file lock on {self.filename}"
                        )
                    time.sleep(0.1)
            yield f
        except IOError as e:
            logger.error(f"IOError when trying to lock file: {e}")
            raise
        finally:
            if f is not None:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    logger.debug(f"File {self.filename} unlocked successfully")
                except IOError as e:
                    logger.error(f"IOError when trying to unlock file: {e}")
                f.close()

    def enqueue(self, item: Any) -> None:
        try:
            item_serialized = jsonpickle.encode(item)
            with self._locked_file("a+") as f:
                f.seek(0)
                size = sum(1 for _ in f)
                if size >= self.max_size:
                    raise ValueError("Queue is full")
                f.seek(0, 2)  # Move to the end of the file
                f.write(item_serialized + "\n")
            logger.debug(f"Item enqueued successfully: {item}")
        except Exception as e:
            logger.debug(f"Failed to enqueue item: {e}")
            raise RuntimeError(f"Failed to enqueue item: {e}")

    def dequeue(self) -> Optional[Any]:
        try:
            with self._locked_file("r+") as f:
                lines = f.readlines()
                if not lines:
                    logger.debug("Queue is empty")
                    return None

                item_serialized = lines[0].strip()
                f.seek(0)
                f.truncate()
                f.writelines(lines[1:])

            item = jsonpickle.decode(item_serialized)
            logger.debug(f"Item dequeued successfully: {item}")
            return item
        except Exception as e:
            logger.debug(f"Failed to dequeue item: {e}")
            raise RuntimeError(f"Failed to dequeue item: {e}")

    def size(self) -> int:
        with self._locked_file("r") as f:
            size = sum(1 for _ in f)
        logger.debug(f"Current queue size: {size}")
        return size

    def clear(self) -> None:
        with self._locked_file("w"):
            pass
        logger.debug("Queue cleared")

    def listen(self, callback: Callable[[Any], None]) -> None:
        while True:
            item = self.dequeue()
            if item:
                callback(item)
