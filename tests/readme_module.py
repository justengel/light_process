import light_process
import multiprocessing as mp


def run():
    print('readme_module')


def run_light_process():
    proc = light_process.LightProcess(target=run)
    proc.start()
    proc.join()


def run_multiprocessing():
    proc = mp.Process(target=run)
    proc.start()
    proc.join()
