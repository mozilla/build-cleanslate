# cleanslate

Records a user's processes at some point in time, and/or, kills any processes
which have been started since the last snapshot was taken. This is useful for resetting an environment periodically without rebooting.

Example:

On the first run the process list is saved to /var/tmp/cleanslate. No processes are killed.

        ./cleanslate.py

A new process is created by someuser...

        top &

The new process is killed, along with any others which were created since the first run.

        ./cleanslave.py
