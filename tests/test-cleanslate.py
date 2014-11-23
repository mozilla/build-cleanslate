# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import tempfile
import cleanslate

import nose

temp_filename = tempfile.mktemp()

def rm_temp_file():
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

def test_pid_exists():
    assert cleanslate.pid_exists(os.getpid()) is True
    assert cleanslate.pid_exists(999999) is False


def test_get_process_list():
    assert os.getpid() in cleanslate.get_process_list(os.getlogin())


@nose.with_setup(setup=None, teardown=rm_temp_file)
def test_get_saved_process_list():
    process_list = cleanslate.get_process_list(os.getlogin())
    cleanslate.save_process_list(process_list, temp_filename)
    assert process_list == cleanslate.get_saved_process_list(temp_filename)
