# cleanslate

Records a user's processes at some point in time, and/or, kills any processes
which have been started since the last snapshot was taken. This is useful for resetting an environment periodically without rebooting.

Example:

    First run, process list is saved to /var/tmp/cleanslate. No processes killed.
    ``./cleanslate.py someuser``

    A new process is created by someuser...
    ``top &``

    The new process is killed, along with any others which were created.
    ``./cleanslave.py someuser``
