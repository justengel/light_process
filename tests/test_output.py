import sys


def print_stdout():
    print('abc')
    print('123')
    print('Hello World!')


def print_stderr():
    print('def', file=sys.stderr)
    print('456', file=sys.stderr)
    print('Goodbye John', file=sys.stderr)


def run_print_stdout():
    import light_process as lp

    print('\n===== Save Ouptut =====')
    proc = lp.Process(target=print_stdout, save_stdout=True)
    proc.start()
    proc.join()

    assert 'abc' in proc.stdout, proc.stdout
    assert '123' in proc.stdout, proc.stdout
    assert 'Hello World!' in proc.stdout, proc.stdout

    print('\n===== Do Not Save Ouptut =====')
    proc = lp.Process(target=print_stdout, save_stdout=False)
    proc.start()
    proc.join()

    assert proc.stdout is None


def run_print_stderr():
    import light_process as lp

    print('\n===== Save Ouptut =====')
    proc = lp.Process(target=print_stderr, save_stderr=True)
    proc.start()
    proc.join()

    assert 'def' in proc.stderr, proc.stderr
    assert '456' in proc.stderr, proc.stderr
    assert 'Goodbye John' in proc.stderr, proc.stderr

    print('\n===== Do Not Save Ouptut =====')
    proc = lp.Process(target=print_stderr, save_stderr=False)
    proc.start()
    proc.join()

    assert proc.stderr is None


def run_normal_mp():
    import light_process as lp

    print('\n===== Save Ouptut =====')
    proc = lp.Process(target=print_stderr, target_module=False, save_stderr=True)
    proc.start()
    proc.join()

    assert 'def' in proc.stderr, proc.stderr
    assert '456' in proc.stderr, proc.stderr
    assert 'Goodbye John' in proc.stderr, proc.stderr

    print('\n===== Do Not Save Ouptut =====')
    proc = lp.Process(target=print_stderr, save_stderr=False)
    proc.start()
    proc.join()

    assert proc.stderr is None

if __name__ == '__main__':
    # run_print_stdout()
    # run_print_stderr()
    run_normal_mp()

    print('All tests finished successfully!')
