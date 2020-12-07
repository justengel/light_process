import os
import sys
import multiprocessing as mp


__all__ = ['FileQueue', 'StdoutQueue', 'StderrQueue']


class FileQueue(object):
    DEFAULT_FILE_HANDLE = None
    SENTINEL = None

    def __init__(self, file=None, connection=None):
        self.file = file or self.DEFAULT_FILE_HANDLE
        self.connection = connection or mp.Pipe(duplex=False)

    def write(self, b):
        """Write the data to the queue/pipe and the file."""
        if self.connection is not None:
            self.put(b)
        if self.file is not None:
            type(self.file).write(self.file, b)  # Same as `io.TextIoWrapper.write(obj, b)`

    def put_sentinel(self):
        """Put the sentinel value on the queue/pipe to indicate no more data will be on the queue/pipe."""
        self.put(self.SENTINEL)

    def iter_all(self):
        """Iterate through all of the queue/pipe data until the SENTINEL is found"""
        while True:
            value = self.get()
            if value != self.SENTINEL:
                yield value
            else:
                break

    def get_all(self):
        """Return all of the output on the queue/pipe."""
        values = tuple(self.iter_all())
        if isinstance(values, str):
            return ''.join(values)
        elif isinstance(values, bytes):
            return b''.join(values)
        return values

    # ===== Queue/Pipe Functions =====
    def empty(self):
        """Return if the queue/pipe is empty."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            return not self.connection[0].poll()
        else:
            return self.connection.empty()

    def full(self):
        """Return if the queue/pipe is full."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            return False
        else:
            return self.connection.full()

    def qsize(self):
        """Return the queue/pipe size."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            return None
        else:
            return self.connection.qsize()

    def put(self, value):
        """Get a value on the queue/pipe."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            self.connection[1].send(value)
        else:
            self.connection.put(value)

    def get(self, *args, **kwargs):
        """Get a value from the queue/pipe."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            return self.connection[0].recv()
        else:
            return self.connection.get(*args, **kwargs)

    def get_nowait(self):
        """Get a value from the queue/pipe."""
        if isinstance(self.connection, tuple):  # Assume pipe.
            return self.connection[0].recv()
        else:
            return self.connection.get_nowait()

    def __getattr__(self, item):
        if hasattr(self.file, item):
            return getattr(self.file, item)

    # ===== Pickle Settings =====
    def get_file_settings(self):
        """Return the settings dictionary for the file."""
        if self.file == self.DEFAULT_FILE_HANDLE:
            return None
        else:
            return {'fileno': self.file.fileno(), 'mode': self.file.mode}

    def open_file_with_settings(self, file=None):
        """Open and set the file with the given dictionary of file settings.

        If the given file settings is None use the class default file handle.
        """
        if isinstance(file, dict):
            fileno = file.pop('fileno')
            mode = file.pop('mode')
            self.file = os.fdopen(fileno, mode)
        elif file is None:
            self.file = self.DEFAULT_FILE_HANDLE
        else:
            self.file = file

    def __getstate__(self):
        d = {'connection': self.connection,
             'file': self.get_file_settings(),
             'SENTINEL': self.SENTINEL,
             }
        return d

    def __setstate__(self, state):
        self.file = None
        self.connection = None

        # Open file
        try:
            self.open_file_with_settings(state.pop('file', None))
        except (KeyError, Exception):
            pass

        # SENTINEL
        sentinel = state.pop('SENTINEL', None)
        if sentinel != self.__class__.SENTINEL:
            self.SENTINEL = sentinel

        # Set the attributes
        for k, v in state.items():
            setattr(self, k, v)


class StdoutQueue(FileQueue):
    DEFAULT_FILE_HANDLE = sys.__stdout__


class StderrQueue(FileQueue):
    DEFAULT_FILE_HANDLE = sys.__stderr__
