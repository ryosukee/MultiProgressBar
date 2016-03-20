import time
import random
from multiprocessing import Process
from mprogressbar import ProgressManager


def hoge(p):
    for i in p('Process A', order=1, maxv=2, nest=0)(range(2)):
        for j in p('Process B', order=2, maxv=2, nest=1)(range(2)):
            num = 0
            for _ in p('Process C', order=3, maxv=15, nest=2)(range(15)):
                num += random.randint(0, 10)
                time.sleep(random.uniform(0.01, 0.2))
            p.print('result C: A:{}, B:{} = {}'.format(i, j, num), order=4+2*i+j, nest=3)
        for _ in p('Process D', order=8, maxv=10, nest=1)(range(10)):
            time.sleep(random.uniform(0.01, 0.2))
            num += random.randint(0, 10)
        p.print('result D: A:{} = {}'.format(i, num), order=9+i, nest=2)

m = ProgressManager()
progress_tree = m.new_tree()
progress_tree2 = m.new_tree(offset=11)
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
