#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
Run some cleanup actions against a user's system.
'''

import logging
log = logging.getLogger(__name__)


def make_argparser(supported_cleaners=None):
    import argparse
    parser = argparse.ArgumentParser(__doc__)

    if supported_cleaners:
        for cleaner in supported_cleaners:
            cleaner.add_arguments(parser)

    parser.add_argument('-q', '--quiet', dest='loglevel', action='store_const', const=logging.WARN, help='quiet')
    parser.add_argument('-v', '--verbose', dest='loglevel', action='store_const', const=logging.DEBUG, help='verbose')
    parser.add_argument('--dryrun', dest='dryrun', action='store_const', const=True)
    return parser


if __name__ == '__main__':
    # We're employing the, usually, not-so-good practice of using import *
    # to encourage registration of all available cleaners supported on the
    # platform with the platform_cleaners.AVAILABLE_CLEANERS set. Supported
    # cleaners are added to the set via metaclass.
    from platform_cleaners.process import *  # noqa

    from platform_cleaners import AVAILABLE_CLEANERS

    parser = make_argparser(AVAILABLE_CLEANERS)
    args = parser.parse_args()
    args_dict = vars(args)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=args.loglevel)

    if args.dryrun:
        log.info('** dry-run mode **')

    for cleaner in AVAILABLE_CLEANERS:
        cleaner(**args_dict).enforce(dryrun=args.dryrun)
