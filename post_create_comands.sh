#!/bin/bash
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

/usr/local/bin/docker-entrypoint.sh postgres &

while pg_isready -U "${POSTGRES_USER:?}" ; ret=$? ; [ $ret -ne 0 ];do
    sleep 1
  done

echo "database is up"
tail -f /dev/null
# python3 insert_every_n_seconds.py "${UPDATE_RATE:?}"
