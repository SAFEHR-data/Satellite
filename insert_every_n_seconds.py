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
import sys
import os
import print_sql_create_command
from time import time, sleep


if __name__ == '__main__':

    N_SECONDS = 1 / float(sys.argv[1])
    os.environ["N_TABLE_ROWS"] = "1"

    while True:
        start_time = time()
        os.system(f"psql -U postgres -c {print_sql_create_command.main()}")
        sleep(N_SECONDS - (time() - start_time))
