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


def test_get_process_set():
    assert os.getpid() in [pid for pid, cmd in cleanslate.get_process_set(os.getlogin())]


@nose.with_setup(setup=None, teardown=rm_temp_file)
def test_get_saved_process_set():
    process_set = cleanslate.get_process_set(os.getlogin())
    cleanslate.save_process_set(process_set, temp_filename)
    assert process_set == cleanslate.get_saved_process_set(temp_filename)
