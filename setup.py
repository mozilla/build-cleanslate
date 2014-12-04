# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

setup(
    name="cleanslate",
    version="1.1",
    description="Reset a users running processes to a previously recorded state.",
    author="Morgan Phillips",
    author_email="winter2718@gmail.com",
    py_packages=[
        "cleanslate",
    ],
    scripts=["cleanslate.py"],
    url="https://github.com/mrrrgn/build-cleanslate",
    setup_requires=["nose==1.3.4"],
)
