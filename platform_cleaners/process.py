# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import time
import errno
import platform
import subprocess

from . import BasePlatformCleaner

import logging
log = logging.getLogger(__name__)


class PosixProcessCleaner(BasePlatformCleaner):
    '''
    Records a user's processes at some point in time, and/or, kills any proccesses
    which have been started since its prior run. This is useful for resetting an
    periodically without rebooting.
    '''

    sub_parser_name = 'process_cleaner'

    for_user = os.environ.get('USER')
    filename = '/var/tmp/cleanslate'

    def __init__(self, for_user=None, filename=None, **kwargs):
        super(PosixProcessCleaner, self).__init__()
        if for_user:
            self.for_user = for_user
        if filename:
            self.filename = filename

    @staticmethod
    def check_platform():
        if platform.system() in ('Darwin', 'Linux'):
            return True

    @classmethod
    def add_arguments(cls, parser, sub_parser):
        processes_parser = sub_parser.add_parser(
            cls.sub_parser_name,
            description='Records a user\'s processes at some point in time, '
            'and/or, kills any proccesses which have been started since its '
            'prior run.'
        )
        processes_parser.add_argument(
            '-U',
            '--user',
            default=os.getenv('USER'),
            help='Clean processes owned by this user.'
        )
        processes_parser.add_argument(
            '-f',
            '--filename',
            default=os.environ.get('CLEANSLATE_FILENAME'),
            help='Location of saved process lists.'
        )

    @classmethod
    def pid_exists(cls, pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError as e:
            if e.errno == errno.ESRCH:
                # If sending the signal fails w/ a process does not exist error
                return False
            else:
                raise e

    @classmethod
    def _parse_ps_line(cls, ps_line):
        '''
        Parse some line of input returned from a ps command and return a tuple:
        (pid, command)
        '''
        ps_line = ps_line.strip().split(None, 1)
        if len(ps_line) > 1 and ps_line[0].isdigit():
            return (int(ps_line[0]), ps_line[1])

    @classmethod
    def get_process_set(cls, for_user):
        '''
        Gather all of the processes running for some user. Returns a set of
        (pid, cmd) tuples: {(pid, cmd), ...}
        '''
        ps_cmd = ['ps', '-o', 'pid args', '-U', for_user]
        ps = subprocess.check_output(ps_cmd)

        process_set = set()
        for ps_line in ps.split(os.linesep)[1:]:
            ps_tuple = cls._parse_ps_line(ps_line)
            if ps_tuple:
                process_set.add(ps_tuple)

        return process_set

    @classmethod
    def save_process_set(cls, process_set, filename):
        '''
        Save the current process list as a csv file.
        '''
        with open(filename, 'w') as process_set_file:
            for pid, cmd in process_set:
                process_set_file.write('{} {}{}'.format(pid, cmd, os.linesep))
        return filename

    @classmethod
    def get_saved_process_set(cls, filename):
        '''
        Returns a saved process set {(pid, cmd), ... }, or None if the file does not exist.
        '''
        process_set = None
        if os.path.exists(filename):
            process_set = set()
            with open(filename, 'r') as process_set_file:
                for ps_line in process_set_file:
                    ps_tuple = cls._parse_ps_line(ps_line)
                    if ps_tuple:
                        process_set.add(ps_tuple)
        return process_set

    @classmethod
    def kill_processes(cls, kill_set, sig=15, dryrun=False):
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
                    if cls.pid_exists(ps):
                        raise Exception('')
                except Exception as e:
                    log.debug('(failed to kill %i via sig %i) %s', ps, sig, e.message)
                    fail_set.add(ps)
        return fail_set

    def enforce(self, dryrun=False):
        '''
        If a saved process_set exists, use that as a PID whitelist, killing
        all processes which are not a part of it. If no such file exists, create
        one. Returns a list of processes which were killed.
        '''
        current_ps = self.get_process_set(self.for_user)
        saved_ps = self.get_saved_process_set(self.filename)

        if not saved_ps:
            log.debug('No saved process list found, creating one at %s',
                      self.save_process_set(current_ps, self.filename))
            return

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

        fail_set = self.kill_processes(kill_set, dryrun=dryrun)
        # if we fail any on the first try, send them a kill -9
        if fail_set:
            fail_set = self.kill_processes(fail_set, sig=9, dryrun=dryrun)

        if fail_set:
            raise Exception('Failed to kill: %s' % fail_set)

        return fail_set.difference(kill_set)
