# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from platform_cleaners import BasePlatformCleaner, AVAILABLE_CLEANERS


class FakeCleanerPassingPlatform(BasePlatformCleaner):
    @staticmethod
    def check_platform():
        return True  # I work on your current platform! :)


class FakeCleanerFailingPlatform(BasePlatformCleaner):
    @staticmethod
    def check_platform():
        return False  # Let's pretend I'm Plan 9


def test_available_cleaners():
    assert len(AVAILABLE_CLEANERS) == 1
    assert FakeCleanerPassingPlatform in AVAILABLE_CLEANERS
    assert FakeCleanerFailingPlatform not in AVAILABLE_CLEANERS
