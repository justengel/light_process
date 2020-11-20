=============
light_process
=============

Python multiprocessing.Process that does not need to import __main__.

Normally python multiprocessing using the __main__ module to create and initiallize the process. The LightProcess
allows you to change what module is used to create and initialize the process. By default the LightProcess uses
the module that calls LightProcess.start()


Example
=======

.. code-block:: python

    # readme_module.py
    import light_process as lp
    import multiprocessing as mp


    def run():
        print('readme_module')


    def run_light_process():
        proc = lp.LightProcess(target=run)
        proc.start()
        proc.join()


    def run_multiprocessing():
        proc = mp.Process(target=run)
        proc.start()
        proc.join()


Multiprocessing works by using the __main__ module to import and seutp the environment for multiprocess. Using the
multiprocessing.Process requires you to put your multiprocessing code in "if __name__ == '__main__':". This can be shown
in the following example.

.. code-block:: python

    # readme_main_multiprocessing.py
    import readme_module


    print('__main__')


    if __name__ == '__main__':
        print("if __name__ == '__main__':")
        readme_module.run_multiprocessing()

    # Output:
    # __main__
    # if __name__ == '__main__':
    # __main__
    # readme_module
    #
    # Note:
    # '__main__' and 'readme_module' will be printed
    # '__main__' will be printed twice, because this module is imported in the other process


The main takeaway form this is that the main module is imported twice and requires you to run you multiprocessing code
in the "if __name__ == '__main__':" block.

LightProcess was made to remove __main__ from being imported. I have large applications that use multiprocessing. I do
not need to load the entire enviroment for the process. I simply need one small module to be imported and run.
The example below shows how you can run the processes in __main__ and how it doesn't import __main__ in the new process.


.. code-block:: python

    # readme_main_light_process.py
    import readme_module


    print('__main__')


    # Do not need "if __name__ == '__main__':"
    readme_module.run_light_process()

    # Output:
    # __main__
    # readme_module
    #
    # Note:
    # '__main__' and 'readme_module' will be printed
    # '__main__' will only be printed once

