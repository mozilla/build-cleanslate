# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# A global set of all PlatformCleaner classes which pass the "check_platform"
# test. Allows cleanslate to work across all platforms with no need for complex
# import code. All children of BasePlatformCleaner will be automagically added
# to it at import time.
AVAILABLE_CLEANERS = set()


class PlatformCleanerMeta(type):
    '''
    Register a cleaner with the AVAILABLE_CLEANERS global if the its
    check_platform method returns True.
    '''
    def __init__(self, name, type, other):
        if self.check_platform():
            AVAILABLE_CLEANERS.add(self)


class BasePlatformCleaner(object):
    '''
    An "Abstract" class for Cleaner objects. Because its metaclass
    is PlatformCleanerMeta, all children of this class will show up
    in the AVAILABLE_CLEANERS set.
    '''

    __metaclass__ = PlatformCleanerMeta

    @staticmethod
    def add_arguments(argument_parser, sub_parser=None):
        '''
        Allows a cleaner to attach new arguments to an arg parser.
        '''
        return argument_parser

    @staticmethod
    def check_platform():
        '''
        This method should ensure that the current platform supports
        whatever cleanup actions will be attempted. When it returns true
        the class will be added to the global AVAILABLE_CLEANERS list.
        '''
        return False

    def enforce(self, dryrun=False):
        '''
        All cleanup actions should be performed in this method, which should also,
        ideally, include a "dryrun" mode.
        '''
        raise NotImplementedError
