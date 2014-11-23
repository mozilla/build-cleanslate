#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''
Records a user's processes at some point in time, and/or, kills any proccesses
which have been started since its prior run. This is useful for resetting an
periodically without rebooting.
'''

import os
import re
import errno
import shlex
import subprocess

import logging
log = logging.getLogger(__name__)


FILENAME_DEFAULT = '/var/tmp/cleanslate'


def pid_exists(pid):
    try:
        # If sending the signal fails, the process does not exist
        os.kill(pid, 0)
        return True
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        else:
            raise e


def get_process_list(for_user):
    '''
    Gather all of the processes running for some user. Only supports posix
    systems.
    '''
    ps_cmd = 'ps -U {}'.format(for_user)
    ps = subprocess.check_output(shlex.split(ps_cmd))
    return {int(p.group(1)) for p in re.finditer(' (\d+) ', ps.replace(os.linesep, ' '))}


def save_process_list(process_list, filename=FILENAME_DEFAULT):
    '''
    Save the current process list as a csv file.
    '''
    with open(filename, 'w') as process_list_file:
        process_list_file.write(','.join([unicode(p) for p in process_list]))
    return True


def get_saved_process_list(filename=FILENAME_DEFAULT):
    '''
    Returns a saved process list as a set, or None if the file does not exist.
    '''
    process_list = None
    if os.path.exists(filename):
        with open(filename, 'r') as process_list_file:
            process_list = {int(p) for p in process_list_file.read().split(',')}
    return process_list


def kill_process_list(kill_set, sig=15, dryrun=False):
    '''
    Kill any processes not in the whitelist. Returns a set of any pids
    which were not successfully killed.
    '''
    fail_set = set()
    for ps in kill_set:
        log.debug('Killing process %i with SIGNAL %i', ps, sig)
        if dryrun is not False:
            try:
                os.kill(ps, sig)
                if pid_exists(ps):
                    raise Exception('')
            except Exception as e:
                log.debug('(failed to kill %i via sig %i) %s', ps, sig, e.message)
                fail_set.add(ps)
    return fail_set


def clean_process_list(for_user, filename=FILENAME_DEFAULT, snapshot=False, dryrun=False):
    '''
    If a saved process_list exists, use that as a PID whitelist, killing
    all processes which are not a part of it. If no such file exists, create
    one. Returns a list of processes which were killed.
    '''
    current_ps = get_process_list(for_user)
    ps_whitelist = get_saved_process_list(filename)
    ps_whitelist.add(os.getpid())  # Otherwise we'll commit suicide!

    if not ps_whitelist:
        log.debug('No saved process list found, creating one at %s', filename)
        save_process_list(current_ps, filename)
        return set()

    if snapshot is True:
        log.debug('Saving a new process list snapshot at %s', filename)
        save_process_list(current_ps, filename)

    kill_set = set(current_ps).difference(set(ps_whitelist))
    fail_set = kill_process_list(kill_set, dryrun=dryrun)
    print(fail_set)
    # if we fail any on the first try, send them a kill -9
    fail_set = kill_process_list(fail_set, sig=9, dryrun=dryrun)
    log.warn('Failed to kill: %s', fail_set)

    return fail_set.difference(kill_set)


def make_argparser():
    import argparse
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        '-U',
        '--user',
        default=os.environ.get('CLEANSLATE_USER', os.getlogin()),
        help='Clean processes owned by this user.'
    )
    parser.add_argument('-q', '--quiet', dest='loglevel', action='store_const', const=logging.WARN, help='quiet')
    parser.add_argument('-v', '--verbose', dest='loglevel', action='store_const', const=logging.DEBUG, help='verbose')
    parser.add_argument(
        '-f',
        '--filename',
        default=os.environ.get('CLEANSLATE_FILENAME', FILENAME_DEFAULT),
        help='Location of saved process lists.'
    )
    parser.add_argument('--snapshot', dest='snapshot', action='store_const', const=True, help='Create a new process list snapshot.')
    parser.add_argument('--dryrun', dest='dryrun', action='store_const', const=True)
    return parser


if __name__ == '__main__':
    parser = make_argparser()
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=args.loglevel)

    if args.dryrun:
        log.info('Running in dry-run mode.')

    killed_processes = clean_process_list(args.user, args.filename, args.snapshot, args.dryrun)
    if killed_processes:
        print('({}): killed processes {}'.format(__name__, killed_processes))
