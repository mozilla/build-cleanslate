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
import time
import errno
import subprocess

import logging
log = logging.getLogger(__name__)


FILENAME_DEFAULT = '/var/tmp/cleanslate'


def pid_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError as e:
        if e.errno == errno.ESRCH:
            # If sending the signal fails w/ a process does not exist error
            return False
        else:
            raise e


def _parse_ps_line(ps_line):
    '''
    Parse some line of input returned from a ps command and return a tuple:
    (pid, command)
    '''
    ps_line = ps_line.strip().split(None, 1)
    if len(ps_line) > 1 and ps_line[0].isdigit():
        return (int(ps_line[0]), ps_line[1])


def get_process_set(for_user):
    '''
    Gather all of the processes running for some user. Returns a set of
    (pid, cmd) tuples: {(pid, cmd), ...}
    '''
    # TODO: Add windows support via ps_cmd='TASKLIST /S localhost /U {}'
    ps_cmd = ['ps', '-o', 'pid args', '-U', for_user]
    ps = subprocess.check_output(ps_cmd)

    process_set = set()
    for ps_line in ps.split(os.linesep)[1:]:
        ps_tuple = _parse_ps_line(ps_line)
        if ps_tuple:
            process_set.add(ps_tuple)

    return process_set


def save_process_set(process_set, filename=FILENAME_DEFAULT):
    '''
    Save the current process list as a csv file.
    '''
    with open(filename, 'w') as process_set_file:
        for pid, cmd in process_set:
            process_set_file.write('{} {}{}'.format(pid, cmd, os.linesep))
    return filename


def get_saved_process_set(filename=FILENAME_DEFAULT):
    '''
    Returns a saved process set {(pid, cmd), ... }, or None if the file does not exist.
    '''
    process_set = None
    if os.path.exists(filename):
        process_set = set()
        with open(filename, 'r') as process_set_file:
            for ps_line in process_set_file:
                ps_tuple = _parse_ps_line(ps_line)
                if ps_tuple:
                    process_set.add(ps_tuple)
    return process_set


def kill_processes(kill_set, sig=15, dryrun=False):
    '''
    Kill any processes not in the whitelist. Returns a set of any pids
    which were not successfully killed.
    '''
    fail_set = set()
    for ps in kill_set:
        log.debug('Killing process %i with SIGNAL %i', ps, sig)
        if not dryrun:
            try:
                os.kill(ps, sig)
                # We should give the process a little time to die before
                # checking to see if we succeeded
                time.sleep(.1)
                if pid_exists(ps):
                    raise Exception('')
            except Exception as e:
                log.debug('(failed to kill %i via sig %i) %s', ps, sig, e.message)
                fail_set.add(ps)
    return fail_set


def clean_process_set(for_user, filename=FILENAME_DEFAULT, snapshot=False, dryrun=False):
    '''
    If a saved process_set exists, use that as a PID whitelist, killing
    all processes which are not a part of it. If no such file exists, create
    one. Returns a list of processes which were killed.
    '''
    current_ps = get_process_set(for_user)
    saved_ps = get_saved_process_set(filename)

    if not saved_ps:
        log.debug('No saved process list found, creating one at %s',
                  save_process_set(current_ps, filename))
        return

    if snapshot:
        log.debug('Saving a new process list snapshot at %s',
                  save_process_set(current_ps, filename))

    kill_set = set()
    self_pid = os.getpid()
    saved_cmds = [cmd for pid, cmd in saved_ps.difference(current_ps)]
    for pid, cmd in set(current_ps).difference(set(saved_ps)):
        if cmd in saved_cmds:
            # by removing we ensure that we will maintain the original number
            # of processes with the same command.
            saved_cmds.remove(cmd)
        elif pid != self_pid:
            log.debug("Adding pid:%i cmd:'%s' to kill set.", pid, cmd)
            kill_set.add(pid)

    fail_set = kill_processes(kill_set, dryrun=dryrun)
    # if we fail any on the first try, send them a kill -9
    if fail_set:
        fail_set = kill_processes(fail_set, sig=9, dryrun=dryrun)

    if fail_set:
        raise Exception('Failed to kill: %s' % fail_set)

    return fail_set.difference(kill_set)


def make_argparser():
    import argparse
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        '-U',
        '--user',
        default=os.getenv('USER'),
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
        log.info('** dry-run mode **')
    clean_process_set(args.user, args.filename, args.snapshot, args.dryrun)
