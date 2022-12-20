import re

from time import time, sleep
from typing import Callable

from satellite._log import logger

# from: https://tinyurl.com/yfv7m927
_camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake_case(string: str) -> str:
    return _camel_case_pattern.sub("_", string).lower()


def call_every_n_seconds(function: Callable, num_seconds: float) -> None:
    """Call a function forever waiting at least num_seconds between each call"""

    while True:

        start_time = time()
        function()
        sleep_time = num_seconds - (time() - start_time)

        if sleep_time < 0:
            logger.warning(f"Cannot call {function} fast enough! Delay time was -ve")
        else:
            sleep(sleep_time)
