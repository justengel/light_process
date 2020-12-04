import os
import sys
import multiprocessing as mp


__all__ = ['FileQueue', 'StdoutQueue', 'StderrQueue']


class FileQueue(object):
    DEFAULT_FILE_HANDLE = None  # Used for stdout or stderr

    def __init__(self, file=None, queue=None):
        self.file = file or self.DEFAULT_FILE_HANDLE
        self.queue = queue or mp.Queue()

    def write(self, b):
        """Write the data to the queue and the file."""
        if self.queue is not None:
            self.queue.put(b)
        if self.file is not None:
            type(self.file).write(self.file, b)  # Same as `io.TextIoWrapper.write(obj, b)`

    # ===== Queue Functions =====
    def empty(self):
        """Return if the queue is empty."""
        return self.queue.empty()

    def full(self):
        """Return if the queue is full."""
        return self.queue.full()

    def qsize(self):
        """Return the queue size."""
        return self.queue.qsize()

    def get(self, *args, **kwargs):
        """Get a value from the queue."""
        return self.queue.get(*args, **kwargs)

    def get_nowait(self):
        """Get a value from the queue."""
        return self.queue.get_nowait()

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
        d = {'queue': self.queue,
             'file': self.get_file_settings(),
             }
        return d

    def __setstate__(self, state):
        self.file = None
        self.queue = None

        try:
            self.open_file_with_settings(state.pop('file', None))
        except (KeyError, Exception):
            pass

        # Set the attributes
        for k, v in state.items():
            setattr(self, k, v)


class StdoutQueue(FileQueue):
    DEFAULT_FILE_HANDLE = sys.__stdout__


class StderrQueue(FileQueue):
    DEFAULT_FILE_HANDLE = sys.__stderr__
