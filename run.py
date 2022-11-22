import threading
import time
import os


def thread_function(index):
    os.system(f'python visa.py --config=config{index}.ini')


if __name__ == "__main__":

    amount_of_accounts = 10
    sleep_time = 60

    for index in range(1, amount_of_accounts + 1):
        x = threading.Thread(target=thread_function, args=(index,))
        x.start()
        time.sleep(sleep_time)
