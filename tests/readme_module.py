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
