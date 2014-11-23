# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import cleanslate


def test_pid_exists():
    assert cleanslate.pid_exists(os.getpid()) is True
    assert cleanslate.pid_exists(999999) is False
