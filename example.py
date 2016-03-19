import time
import random
from multiprocessing import Process
from multi_progressbar import ProgressManager


def hoge(p):
    for _ in p('Progress1', order=1, maxv=2, nest=0)(range(2)):
        for _ in p('Progress2', order=2, maxv=3, nest=1)(range(3)):
            for _ in p('Progress3', order=3, maxv=3, nest=2)(range(3)):
                time.sleep(random.random())
        for _ in p('Progress4', order=4, maxv=3, nest=1)(range(3)):
            time.sleep(random.random())

m = ProgressManager()
progress_tree = m.new_tree()
progress_tree2 = m.new_tree(offset=5)
args = [progress_tree, progress_tree2]
processes = list()
print('start')
m.start()
for i in range(2):
    p = Process(target=hoge, args=(args[i],))
    processes.append(p)
    p.start()
for p in processes:
    p.join()
m.finish()
print('finish')
