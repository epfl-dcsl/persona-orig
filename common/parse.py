# Copyright 2019 École Polytechnique Fédérale de Lausanne. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
from argparse import ArgumentTypeError

def yes_or_no(question):
    # could this overflow the stack if the user was very persistent?
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Please enter ")

def numeric_min_checker(minimum, message, numeric_type=int):
    def check_number(n):
        n = numeric_type(n)
        if n < minimum:
            raise ArgumentTypeError("{msg}: got {got}, minimum is {minimum}".format(
                msg=message, got=n, minimum=minimum
            ))
        return n
    return check_number

def path_exists_checker(check_dir=True, make_absolute=True, make_if_empty=False):
    def _func(path):
        path = os.path.expanduser(path)
        if os.path.exists(path):
            if check_dir:
                if not os.path.isdir(path):
                    raise ArgumentTypeError("path {pth} exists, but isn't a directory".format(pth=path))
            elif not os.path.isfile(path=path):
                raise ArgumentTypeError("path {pth} exists, but isn't a file".format(pth=path))
        elif check_dir and make_if_empty:
            os.makedirs(name=path)
        else:
            raise ArgumentTypeError("path {pth} doesn't exist on filesystem".format(pth=path))
        if make_absolute:
            path = os.path.abspath(path=path)
        return path
    return _func

def non_empty_string_checker(string):
    if len(string) == 0:
        raise ArgumentTypeError("string is empty!")
    return string
