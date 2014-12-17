# cleanslate

Cleanslate performs platform specific cleanup actions via "cleaner" modules. Each module works to provide a fresh environment without the need for a reboot.

# cleaners

## Process Cleaner (Darwin, Linux)

Records a user's processes at some point in time, and/or, kills any processes
which have been started since the last snapshot was taken.

### Arguments

    `-U, --user` Work on processes own by this particular user. Defaults to ${USER}
    `-f, --filename` Location of process snapshot file. Defaults to /var/tmp/cleanslate

### Which processes are killed?

Processes are whitelisted based on their name + arguments *not* by pid. This prevents managed processes which die and are restarted from being killed by cleanslate. That being the case, cleanslate will enforce that no more than the original number of processes are allowed to run.

So, if a snapshot is taken where the same file is opened twice:

        PID COMMAND
        4   vim a.py
        5   vim a.py

Cleanslate will ensure that, on its next run, no more than two processes with the command 'vim a.py' are running.

### How are processes killed?

On Posix systems cleanslate will attempt to kill processes via SIGTERM (in hopes of a graceful shutdown). If this fails it will try once more with a SIGKILL.

### Example:

On the first run the process list is saved to /var/tmp/cleanslate. No processes are killed.

        ./cleanslate.py -v
        2014-11-23 23:38:44,316 - DEBUG - No saved process list found, creating one at /var/tmp/cleanslate

A new process is created by someuser...

        top &

The new process is killed, along with any others which were created since the first run.

        ./cleanslate.py -v
        2014-11-23 23:29:45,364 - DEBUG - Adding pid:26168 cmd:'top' to kill set.
        2014-11-23 23:29:45,364 - DEBUG - Killing process 26168 with SIGNAL 15
        2014-11-23 23:29:45,374 - DEBUG - (failed to kill 26168 via sig 15)
        2014-11-23 23:29:45,375 - DEBUG - Killing process 26168 with SIGNAL 9
