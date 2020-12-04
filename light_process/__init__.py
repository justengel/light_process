from light_process.__meta__ import version as __version__
from light_process.utils import FileQueue, StdoutQueue, StderrQueue

import sys
import inspect
import contextlib
import multiprocessing as mp
from multiprocessing import *

try:
    mp_all = mp.__all__
except (AttributeError, Exception):
    mp_all = []


__all__ = mp_all + ['LightProcess', 'Process', 'freeze_support', 'MpProcess',
                    'FileQueue', 'StdoutQueue', 'StderrQueue']


MpProcess = mp.Process
FREEZE_CALLED = False
mp_freeze_support = freeze_support


def has_freeze_support():
    """Return if freeze_support was called."""
    global FREEZE_CALLED
    return FREEZE_CALLED


def freeze_support():
    """You do not need to call this function.

    Spawns a new process here and quits the current process. This allows executables to spawn new processes without
    infinite recursion.
    """
    global FREEZE_CALLED
    if not FREEZE_CALLED:
        mp_freeze_support()
        FREEZE_CALLED = True


mp.freeze_support = freeze_support


def run_with_output(*args, **kwargs):
    """Run the main multiprocessing function while saving stdout and/or stderr."""
    # Get variables
    target = kwargs.pop('LP_TARGET_FUNC')  # Raise Error. Do not use this if a target was not given
    out_queue = kwargs.pop('LP_STDOUT_QUEUE', None)
    err_queue = kwargs.pop('LP_STDERR_QUEUE', None)

    # Save output
    if out_queue:
        sys.stdout = out_queue
    if err_queue:
        sys.stderr = err_queue

    # Run the function
    target(*args, **kwargs)

    # Reset output
    if out_queue:
        sys.stdout = sys.__stdout__
    if err_queue:
        sys.stderr = sys.__stderr__


class LightProcess(MpProcess):
    """Process that only uses the specified module or the module that creates the LightProcess object.

    Args:
        group (None)[None]: The group should always be None; it exists solely for compatibility with threading.Thread.
        target (function/callable): is the callable object to be invoked by the run() method.
        name (str)[None]: is the process name.
        args (tuple)[tuple()]: is the argument tuple for the target invocation.
        kwargs (dict)[{}]: is a dictionary of keyword arguments for the target invocation.
        daemon (bool)[None]: sets the process daemon flag to True or False. If None (the default) this flag will be
            inherited from the creating process.
        target_module (ModuleType)[None]: Module to import. The multiprocessing.Process uses '__main__'. This allows
            you to only import a smaller portion of code for your process.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None,
                 target_module=None, save_stdout=False, save_stderr=False):
        """Process that only uses the specified module or the module that creates the LightProcess object.

        Args:
            group (None)[None]: The group should always be None; it exists solely for compatibility with threading.Thread.
            target (function/callable): is the callable object to be invoked by the run() method.
            name (str)[None]: is the process name.
            args (tuple)[tuple()]: is the argument tuple for the target invocation.
            kwargs (dict)[{}]: is a dictionary of keyword arguments for the target invocation.
            daemon (bool)[None]: sets the process daemon flag to True or False. If None (the default) this flag will be
                inherited from the creating process.
            target_module (ModuleType)[None]: Module to import. The multiprocessing.Process uses '__main__'. This allows
                you to only import a smaller portion of code for your process.
            save_stdout (bool)[False]: If True use a queue to save stdout.
            save_stderr (bool)[False]: If True use a queue to save stderr.
        """
        self._target_module = target_module
        self.save_stdout = save_stdout
        self.save_stderr = save_stderr
        self.stdout = None
        self.stderr = None
        super(LightProcess, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)

    def start(self):
        """Start the process’s activity.

        This must be called at most once per process object. It arranges for the object’s run() method to be invoked
        in a separate process.
        """
        # Make sure freeze_support was called before starting your first LightProcess.
        if getattr(sys, 'frozen', False) and not has_freeze_support():
            freeze_support()

        # Setup the main module
        if self._target_module is None:
            self._target_module = inspect.getmodule(inspect.currentframe().f_back)

        with self.change_main():
            # Try to change to save output
            self.setup_output()

            # Start the process
            super(LightProcess, self).start()

        return self

    def join(self, timeout=None):
        """Wait until child process terminates

        Args:
            timeout (float/int)[None]: Time to wait for the process to terminate.
        """
        super(LightProcess, self).join(timeout)
        self.teardown_output()

    @contextlib.contextmanager
    def change_main(self):
        """Change sys.modules['__main__'] to the target module for this block."""
        if self._target_module is None:
            # Do not change main for the block
            yield

        else:
            # Change main for the block
            orig = sys.modules['__main__']

            # Check target spec
            if getattr(self._target_module, '__spec__', None) is None:
                self._target_module.__spec__ = getattr(orig, '__spec__', None)

            # Change __main__
            sys.modules['__main__'] = self._target_module
            del self._target_module  # Cannot pickle module object

            try:
                yield
            finally:
                # Reset __main__
                self._target_module = sys.modules['__main__']  # Re-save the target module
                sys.modules['__main__'] = orig

    def setup_output(self):
        """Change what function is running to allow for saving the output."""
        if self.save_stdout or self.save_stderr:
            self._orig_kwargs = getattr(self, '_kwargs', {}).copy()

            # Get the output queues
            self._out_queue = None
            self._err_queue = None
            if self.save_stdout:
                self._kwargs['LP_STDOUT_QUEUE'] = self._out_queue = StdoutQueue()
            if self.save_stderr:
                self._kwargs['LP_STDERR_QUEUE'] = self._err_queue = StderrQueue()

            # Pass the target function into the run_with_output function
            self._kwargs['LP_TARGET_FUNC'] = self._target
            self._target = run_with_output

    def teardown_output(self):
        """Change the function back to the original after saving the output."""
        if self.save_stdout or self.save_stderr:
            self._kwargs = self._orig_kwargs
            if self._err_queue:
                self.stderr = ''.join((self._err_queue.get() for _ in range(self._err_queue.qsize())))
            if self._out_queue:
                self.stdout = ''.join((self._out_queue.get() for _ in range(self._out_queue.qsize())))

            try:
                del self._orig_kwargs
            except (AttributeError, Exception):
                pass
            try:
                del self._err_queue
            except (AttributeError, Exception):
                pass
            try:
                del self._out_queue
            except (AttributeError, Exception):
                pass


Process = LightProcess


