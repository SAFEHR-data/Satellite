#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
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
