import logging
import time
from typing import Any, Callable, Optional
from functools import wraps
import threading


class BlockTimer:
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        logging.info(f"Starting {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_time = time.time() - self.start_time
        logging.info(f"{self.name} - elapsed time: {elapsed_time:.2f}s")


def method_timer(method: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = method(self, *args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger = logging.getLogger(self.__class__.__name__)
        logger.info(f"Method {method.__name__} executed in {elapsed_time:.2f}s")
        return result

    return wrapper


def log_method_call(method: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger(self.__class__.__name__)
        logger.info(f"Called method {method.__name__}")
        return method(self, *args, **kwargs)

    return wrapper


class SingletonMeta(type):
    _instance: Optional["SingletonMeta"] = None
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
