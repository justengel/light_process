from light_process.__meta__ import version as __version__

import sys
import inspect
import multiprocessing as mp
from multiprocessing import *

try:
    mp_all = mp.__all__
except (AttributeError, Exception):
    mp_all = []


__all__ = mp_all + ['LightProcess', 'Process', 'freeze_support', 'MpProcess']


MpProcess = mp.Process
FREEZE_CALLED = False


def freeze_support():
    """You do not need to call this function.

    Spawns a new process here and quits the current process. This allows executables to spawn new processes without
    infinite recursion.
    """
    global FREEZE_CALLED
    if not FREEZE_CALLED:
        mp.freeze_support()
        FREEZE_CALLED = True


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
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={},
                 *, daemon=None, target_module=None):
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
        self._target_module = target_module
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)

    def start(self):
        """Start the process’s activity.

        This must be called at most once per process object. It arranges for the object’s run() method to be invoked
        in a separate process.
        """
        # Make sure freeze_support was called before starting your first LightProcess.
        freeze_support()

        # Setup the main module
        if self._target_module is None:
            self._target_module = inspect.getmodule(inspect.currentframe().f_back)
        orig = sys.modules['__main__']
        if getattr(self._target_module, '__spec__', None) is None:
            self._target_module.__spec__ = getattr(orig, '__spec__', None)
        sys.modules['__main__'] = self._target_module
        del self._target_module  # Cannot pickle module object

        # Start the process
        super().start()

        # Reset the main module
        self._target_module = sys.modules['__main__']  # Re-save the target module
        sys.modules['__main__'] = orig
        return self


Process = LightProcess
