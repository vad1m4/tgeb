from typing import Callable, Any
from time import sleep  # type: ignore
import logging

logger = logging.getLogger("general")


# def retry(func: Callable, int) -> None:
#     attempts = 5
#     while attempts != 0:
#         try:
#             func(args)
#             break
#         except Exception as e:
#             logger.warning(f"Error running {func.__name__}: {e}")
#             attempts -= 1
#             sleep(5)
#     logger.error(f"Failed running {func.__name__}: exceeded retry attempts")


# @retry
# def error_func(arg1: int):
#     print(arg1)
#     raise ValueError


# error_func(5)
